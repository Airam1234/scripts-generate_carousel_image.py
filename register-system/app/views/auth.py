from datetime import timedelta

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from ..audit import audit
from ..extensions import db
from ..models import User
from ..security import is_safe_next, password_problems
from ..timeutil import now

bp = Blueprint("auth", __name__)

# Used so unknown emails take as long to reject as wrong passwords.
_DUMMY_HASH = generate_password_hash("not-a-real-password")
GENERIC_ERROR = "Incorrect email or password."


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        cfg = current_app.config

        if user is None:
            check_password_hash(_DUMMY_HASH, password)
            audit("auth.login_failed", summary=f"Unknown account {email[:100]}")
            db.session.commit()
            flash(GENERIC_ERROR, "error")
        elif user.is_locked:
            audit("auth.login_locked", user, f"Login attempted while locked: {user.email}")
            db.session.commit()
            flash("This account is temporarily locked after too many failed attempts. "
                  "Try again later or ask an administrator to unlock it.", "error")
        elif user.check_password(password) and user.is_active:
            user.failed_logins = 0
            user.locked_until = None
            user.last_login_at = now()
            session.clear()
            login_user(user)
            session.permanent = True
            audit("auth.login", user, f"{user.email} signed in", user=user)
            db.session.commit()
            target = request.args.get("next")
            return redirect(target if is_safe_next(target) else url_for("main.dashboard"))
        else:
            if user.check_password(password):
                summary = f"Login to inactive/expired account {user.email}"
            else:
                user.failed_logins += 1
                summary = f"Failed login for {user.email} ({user.failed_logins})"
                if user.failed_logins >= cfg["MAX_FAILED_LOGINS"]:
                    user.locked_until = now() + timedelta(minutes=cfg["LOCKOUT_MINUTES"])
                    user.failed_logins = 0
                    summary += " – account locked"
            audit("auth.login_failed", user, summary)
            db.session.commit()
            flash(GENERIC_ERROR, "error")
    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    audit("auth.logout", current_user, f"{current_user.email} signed out")
    db.session.commit()
    logout_user()
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/account/password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        errors = []
        if not current_user.check_password(current):
            errors.append("Your current password is incorrect.")
        if new != confirm:
            errors.append("New passwords do not match.")
        if new == current:
            errors.append("Choose a password different from your current one.")
        errors += password_problems(new, current_user.email)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            user = current_user._get_current_object()
            user.set_password(new)
            user.must_change_password = False
            audit("auth.password_changed", user, f"{user.email} changed their password")
            db.session.commit()
            login_user(user)  # session id rotated with the new login_id
            flash("Password updated.", "success")
            return redirect(url_for("main.dashboard"))
    return render_template("auth/change_password.html")
