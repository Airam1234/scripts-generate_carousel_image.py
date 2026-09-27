import logging
import secrets
import threading
import time

from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extensions import csrf, db, login_manager

log = logging.getLogger(__name__)

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
        "object-src 'none'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'"
    ),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cache-Control": "no-store",
}


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    if not app.config.get("SECRET_KEY"):
        if app.config["APP_ENV"] == "production":
            raise RuntimeError("SECRET_KEY must be set in production")
        app.config["SECRET_KEY"] = secrets.token_hex(32)
        log.warning("SECRET_KEY not set – using a random key (sessions reset on restart)")

    if app.config["TRUST_PROXY"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.session_protection = "strong"

    from . import models

    @login_manager.user_loader
    def load_user(login_id):
        return models.User.query.filter_by(login_id=login_id).first()

    from .views import admin, auth, cohorts, learners, main, pastoral, reports, sessions
    for module in (auth, main, admin, cohorts, learners, sessions, pastoral, reports):
        app.register_blueprint(module.bp)

    _register_hooks(app)
    _register_template_helpers(app)
    _register_errors(app)

    from .cli import register_cli
    register_cli(app)

    with app.app_context():
        db.create_all()
        models.seed_courses()

    if app.config["ENABLE_SCHEDULER"] and not app.config.get("TESTING"):
        _start_scheduler(app)
    return app


def _register_hooks(app):
    from flask import session
    from flask_login import current_user

    @app.before_request
    def keep_session_alive():
        session.permanent = True  # idle timeout = PERMANENT_SESSION_LIFETIME

    @app.before_request
    def force_password_change():
        from flask import redirect, url_for
        if (
            current_user.is_authenticated
            and current_user.must_change_password
            and request.endpoint not in {"auth.change_password", "auth.logout", "static"}
        ):
            return redirect(url_for("auth.change_password"))
        return None

    @app.after_request
    def security_headers(response):
        for name, value in SECURITY_HEADERS.items():
            if name == "Cache-Control" and request.endpoint == "static":
                continue
            response.headers.setdefault(name, value)
        if request.is_secure or app.config["SESSION_COOKIE_SECURE"]:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


def _register_template_helpers(app):
    from . import models, timeutil

    @app.context_processor
    def inject():
        return {
            "Role": models.Role,
            "AttendanceStatus": models.AttendanceStatus,
            "SessionType": models.SessionType,
            "org_name": app.config["ORGANISATION_NAME"],
            "now": timeutil.now(),
        }

    @app.template_filter("dt")
    def format_dt(value, fmt="%d/%m/%Y %H:%M"):
        return value.strftime(fmt) if value else ""

    @app.template_filter("d")
    def format_d(value):
        return value.strftime("%d/%m/%Y") if value else ""

    @app.template_filter("pct")
    def format_pct(value):
        return "–" if value is None else f"{value:.1f}%"


def _register_errors(app):
    @app.errorhandler(403)
    def forbidden(_):
        return render_template("errors/error.html", code=403, message="You do not have access to this page."), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/error.html", code=404, message="Page not found."), 404

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/error.html", code=400, message=getattr(e, "description", "Bad request.")), 400


def _start_scheduler(app):
    """Lightweight in-process job that runs the 15-minute pastoral check.

    Each worker runs one; the check claims sessions atomically so running it
    in several processes is safe. `flask process-alerts` can be used from
    cron instead (set ENABLE_SCHEDULER=0).
    """
    from .notifications import process_due_sessions

    interval = app.config["SCHEDULER_INTERVAL_SECONDS"]

    def loop():
        while True:
            time.sleep(interval)
            try:
                with app.app_context():
                    process_due_sessions()
            except Exception:  # noqa: BLE001
                log.exception("Pastoral alert check failed")
                with app.app_context():
                    db.session.rollback()

    threading.Thread(target=loop, name="pastoral-alerts", daemon=True).start()
