import io
import secrets
from datetime import datetime, timedelta

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..audit import audit, diff
from ..extensions import db
from ..models import AuditLog, Cohort, Course, EmailLog, Role, TrainingSession, User
from ..reports import SafeCSVWriter
from ..security import roles_required
from ..timeutil import now

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _temp_password():
    return secrets.token_urlsafe(12)


def _parse_expiry(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d") + timedelta(hours=23, minutes=59)
    except ValueError:
        return "invalid"


# ---- users (tutors, pastoral, admins, inspectors) -------------------------------

@bp.route("/users")
@roles_required(Role.ADMIN)
def users():
    role = request.args.get("role")
    q = User.query
    if role in Role.ALL:
        q = q.filter_by(role=role)
    return render_template("admin/users.html", users=q.order_by(User.active.desc(), User.name).all(), role=role)


@bp.route("/users/new", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def user_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role")
        expires = _parse_expiry(request.form.get("expires_at"))
        errors = []
        if not name or not email or "@" not in email:
            errors.append("Name and a valid email are required.")
        if role not in Role.ALL:
            errors.append("Choose a role.")
        if expires == "invalid":
            errors.append("Expiry date is invalid.")
        if User.query.filter_by(email=email).first():
            errors.append("A user with that email already exists.")
        if not errors:
            password = _temp_password()
            user = User(name=name, email=email, role=role, expires_at=expires, must_change_password=True)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            audit("user.created", user, f"Created {Role.LABELS[role]} {name} <{email}>",
                  {"role": role, "expires_at": expires})
            db.session.commit()
            return render_template("admin/temp_password.html", user=user, password=password)
        for e in errors:
            flash(e, "error")
    return render_template("admin/user_form.html", user=None)


@bp.route("/users/<int:user_id>", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def user_edit(user_id):
    user = db.get_or_404(User, user_id)
    if request.method == "POST":
        action = request.form.get("action", "save")
        if action == "reset_password":
            password = _temp_password()
            user.set_password(password)
            user.must_change_password = True
            user.failed_logins = 0
            user.locked_until = None
            audit("user.password_reset", user, f"Password reset for {user.email}")
            db.session.commit()
            return render_template("admin/temp_password.html", user=user, password=password)
        if action == "unlock":
            user.failed_logins = 0
            user.locked_until = None
            audit("user.unlocked", user, f"Unlocked {user.email}")
            db.session.commit()
            flash("Account unlocked.", "success")
            return redirect(url_for("admin.user_edit", user_id=user.id))

        expires = _parse_expiry(request.form.get("expires_at"))
        role = request.form.get("role")
        active = request.form.get("active") == "on"
        name = request.form.get("name", "").strip()
        if expires == "invalid" or role not in Role.ALL or not name:
            flash("Please check the form – name, role and expiry must be valid.", "error")
        elif user.id == current_user.id and (not active or role != Role.ADMIN):
            flash("You cannot deactivate yourself or remove your own admin rights.", "error")
        else:
            changes = diff(user, ["name", "role", "active", "expires_at"],
                           {"name": name, "role": role, "active": active, "expires_at": expires})
            if changes:
                if "active" in changes and not active:
                    user.login_id = secrets.token_hex(32)  # end any live sessions
                audit("user.updated", user, f"Updated {user.email}", changes)
                db.session.commit()
                flash("User updated.", "success")
            return redirect(url_for("admin.users"))
    cohorts = Cohort.query.filter_by(tutor_id=user.id, active=True).all()
    upcoming = TrainingSession.query.filter(
        TrainingSession.tutor_id == user.id, TrainingSession.start_at >= now(),
        TrainingSession.cancelled_at.is_(None),
    ).count()
    return render_template("admin/user_form.html", user=user, cohorts=cohorts, upcoming=upcoming)


# ---- courses --------------------------------------------------------------------

@bp.route("/courses", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def courses():
    if request.method == "POST":
        course_id = request.form.get("course_id", type=int)
        name = request.form.get("name", "").strip()
        level = request.form.get("level", type=int)
        ref = request.form.get("standard_ref", "").strip().upper() or None
        active = request.form.get("active") == "on"
        if not name or not level or not 1 <= level <= 7:
            flash("Course name and a level from 1 to 7 are required.", "error")
        elif course_id:
            course = db.get_or_404(Course, course_id)
            changes = diff(course, ["name", "level", "standard_ref", "active"],
                           {"name": name, "level": level, "standard_ref": ref, "active": active})
            if changes:
                audit("course.updated", course, f"Updated course {course.title}", changes)
                db.session.commit()
                flash("Course updated.", "success")
        else:
            course = Course(name=name, level=level, standard_ref=ref, active=True)
            db.session.add(course)
            db.session.flush()
            audit("course.created", course, f"Added course {course.title}")
            db.session.commit()
            flash("Course added.", "success")
        return redirect(url_for("admin.courses"))
    return render_template("admin/courses.html", courses=Course.query.order_by(Course.name, Course.level).all())


# ---- audit & email logs ---------------------------------------------------------

def _audit_query():
    q = AuditLog.query
    if request.args.get("entity_type"):
        q = q.filter(AuditLog.entity_type == request.args["entity_type"])
    if request.args.get("entity_id", type=int):
        q = q.filter(AuditLog.entity_id == request.args.get("entity_id", type=int))
    if request.args.get("user_id", type=int):
        q = q.filter(AuditLog.user_id == request.args.get("user_id", type=int))
    if request.args.get("action"):
        q = q.filter(AuditLog.action.like(request.args["action"].strip() + "%"))
    for arg, op in (("from", "ge"), ("to", "lt")):
        value = request.args.get(arg)
        if value:
            try:
                day = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                abort(400)
            q = q.filter(AuditLog.at >= day if op == "ge" else AuditLog.at < day + timedelta(days=1))
    return q.order_by(AuditLog.id.desc())


@bp.route("/audit")
@roles_required(Role.ADMIN, Role.INSPECTOR)
def audit_log():
    page = request.args.get("page", 1, type=int)
    entries = _audit_query().paginate(page=page, per_page=100, error_out=False)
    entity_types = [t for (t,) in db.session.query(AuditLog.entity_type).distinct() if t]
    args = {k: v for k, v in request.args.items() if k != "page" and v}
    return render_template("audit/list.html", entries=entries, entity_types=sorted(entity_types), args=args,
                           users=User.query.order_by(User.name).all())


@bp.route("/audit.csv")
@roles_required(Role.ADMIN, Role.INSPECTOR)
def audit_csv():
    buf = io.StringIO()
    w = SafeCSVWriter(buf)
    w.writerow(["id", "timestamp", "user", "action", "entity_type", "entity_id", "summary", "details", "ip"])
    for e in _audit_query().limit(50000):
        w.writerow([e.id, e.at.isoformat(), e.user_label, e.action, e.entity_type, e.entity_id,
                    e.summary, e.details or "", e.ip_address or ""])
    audit("report.exported", summary="Exported audit log CSV")
    db.session.commit()
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=audit-log.csv"})


@bp.route("/emails")
@roles_required(Role.ADMIN)
def emails():
    return render_template("admin/emails.html", emails=EmailLog.query.order_by(EmailLog.id.desc()).limit(200).all())
