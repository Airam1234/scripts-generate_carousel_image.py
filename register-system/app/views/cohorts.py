from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..audit import audit, diff
from ..extensions import db
from ..models import Cohort, Course, LearnerAssignment, Role, TrainingSession, User
from ..security import can_view_cohort, roles_required
from ..services import change_cohort_tutor

bp = Blueprint("cohorts", __name__, url_prefix="/cohorts")


def active_tutors():
    return User.query.filter_by(role=Role.TUTOR, active=True).order_by(User.name).all()


@bp.route("/")
@login_required
def list_cohorts():
    q = Cohort.query
    if current_user.role == Role.TUTOR:
        q = q.filter_by(tutor_id=current_user.id)
    show = request.args.get("show", "active")
    if show != "all":
        q = q.filter_by(active=True)
    course_id = request.args.get("course_id", type=int)
    if course_id:
        q = q.filter_by(course_id=course_id)
    cohorts = q.order_by(Cohort.start_date.desc(), Cohort.name).all()
    return render_template("cohorts/list.html", cohorts=cohorts, courses=Course.query.order_by(Course.name).all(),
                           show=show, course_id=course_id)


def _form_values():
    errors = []
    name = request.form.get("name", "").strip()
    course = db.session.get(Course, request.form.get("course_id", type=int) or 0)
    tutor_id = request.form.get("tutor_id", type=int)
    tutor = db.session.get(User, tutor_id) if tutor_id else None
    try:
        start_date = datetime.strptime(request.form.get("start_date", ""), "%Y-%m-%d").date()
    except ValueError:
        start_date = None
        errors.append("Enter a valid start date.")
    if not name:
        errors.append("Cohort name is required.")
    if course is None:
        errors.append("Choose a course.")
    if tutor is not None and tutor.role != Role.TUTOR:
        errors.append("Assigned tutor must have the Tutor role.")
    return errors, {"name": name, "course": course, "tutor": tutor, "start_date": start_date}


@bp.route("/new", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def new():
    if request.method == "POST":
        errors, v = _form_values()
        if Cohort.query.filter_by(name=v["name"]).first():
            errors.append("A cohort with that name already exists.")
        if not errors:
            cohort = Cohort(name=v["name"], course=v["course"], tutor=v["tutor"], start_date=v["start_date"])
            db.session.add(cohort)
            db.session.flush()
            audit("cohort.created", cohort, f"Created cohort {cohort.name} ({cohort.course.title})",
                  {"tutor": v["tutor"].email if v["tutor"] else None, "start_date": v["start_date"]})
            db.session.commit()
            flash("Cohort created.", "success")
            return redirect(url_for("cohorts.detail", cohort_id=cohort.id))
        for e in errors:
            flash(e, "error")
    return render_template("cohorts/form.html", cohort=None, courses=Course.query.filter_by(active=True).all(),
                           tutors=active_tutors())


@bp.route("/<int:cohort_id>/edit", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def edit(cohort_id):
    cohort = db.get_or_404(Cohort, cohort_id)
    if request.method == "POST":
        errors, v = _form_values()
        clash = Cohort.query.filter(Cohort.name == v["name"], Cohort.id != cohort.id).first()
        if clash:
            errors.append("A cohort with that name already exists.")
        new_tutor = v["tutor"]
        tutor_changed = (new_tutor.id if new_tutor else None) != cohort.tutor_id
        reason = request.form.get("reason", "").strip()
        if tutor_changed and cohort.tutor_id and not reason:
            errors.append("Give a reason for changing the cohort's tutor (kept in the audit trail).")
        if not errors:
            changes = diff(cohort, ["name", "course_id", "start_date", "active"], {
                "name": v["name"], "course_id": v["course"].id, "start_date": v["start_date"],
                "active": request.form.get("active") == "on",
            })
            if changes:
                audit("cohort.updated", cohort, f"Updated cohort {cohort.name}", changes)
            if tutor_changed:
                moved_l, moved_s = change_cohort_tutor(
                    cohort, new_tutor, reason or "Initial tutor assignment", current_user,
                    move_learners=request.form.get("move_learners") == "on",
                    move_sessions=request.form.get("move_sessions") == "on",
                )
                flash(f"Tutor changed. {moved_l} learner(s) and {moved_s} future session(s) moved.", "success")
            db.session.commit()
            return redirect(url_for("cohorts.detail", cohort_id=cohort.id))
        for e in errors:
            flash(e, "error")
    return render_template("cohorts/form.html", cohort=cohort, courses=Course.query.all(), tutors=active_tutors())


@bp.route("/<int:cohort_id>")
@login_required
def detail(cohort_id):
    cohort = db.get_or_404(Cohort, cohort_id)
    if not can_view_cohort(current_user, cohort):
        abort(403)
    sessions = TrainingSession.query.filter_by(cohort_id=cohort.id).order_by(TrainingSession.start_at.desc()).all()
    history = (
        LearnerAssignment.query.filter_by(cohort_id=cohort.id)
        .order_by(LearnerAssignment.assigned_at.desc()).limit(100).all()
    )
    return render_template("cohorts/detail.html", cohort=cohort, sessions=sessions, history=history)
