from functools import wraps
from urllib.parse import urlsplit

from flask import abort, current_app
from flask_login import current_user, login_required

from .models import Role

COMMON_PASSWORDS = {
    "password1234", "password12345", "passwordpassword", "123456789012",
    "qwertyuiop12", "letmein12345", "welcome12345", "apprenticeship",
}


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def password_problems(password, email=""):
    problems = []
    min_len = current_app.config["MIN_PASSWORD_LENGTH"]
    if len(password) < min_len:
        problems.append(f"Password must be at least {min_len} characters.")
    if password.lower() in COMMON_PASSWORDS:
        problems.append("That password is too common.")
    if email and password.lower() == email.lower():
        problems.append("Password must not be your email address.")
    if len(set(password)) < 5:
        problems.append("Password is too repetitive.")
    return problems


def is_safe_next(target):
    if not target:
        return False
    parts = urlsplit(target)
    return not parts.scheme and not parts.netloc and target.startswith("/") and not target.startswith("//")


# ---- record-level access rules -------------------------------------------------

STAFF_WIDE = (Role.ADMIN, Role.PASTORAL, Role.INSPECTOR)


def can_view_cohort(user, cohort):
    return user.role in STAFF_WIDE or cohort.tutor_id == user.id


def can_view_learner(user, learner):
    if user.role in STAFF_WIDE:
        return True
    return learner.tutor_id == user.id or learner.cohort.tutor_id == user.id


def can_view_session(user, session):
    return user.role in STAFF_WIDE or session.tutor_id == user.id or session.cohort.tutor_id == user.id


def can_mark_session(user, session):
    return user.role == Role.ADMIN or (user.role == Role.TUTOR and session.tutor_id == user.id)
