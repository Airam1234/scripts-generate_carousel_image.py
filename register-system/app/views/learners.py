import re
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..audit import audit, diff
from ..extensions import db
from ..models import (
    Attendance,
    AuditLog,
    Cohort,
    Course,
    Learner,
    LearnerStatus,
    LeaveReason,
    PastoralAlert,
    Role,
    TrainingSession,
    User,
)
from ..reports import Tally
from ..security import can_view_learner, roles_required
from ..services import place_learner, reassign_learner
from ..timeutil import now, today

bp = Blueprint("learners", __name__, url_prefix="/learners")

EDITABLE = ["first_name", "last_name", "uln", "email", "phone", "employer_name", "employer_contact",
            "start_date", "planned_end_date", "status"]


def _date(field, required=False, errors=None):
    value = request.form.get(field, "").strip()
    if not value:
        if required and errors is not None:
            errors.append(f"{field.replace('_', ' ').capitalize()} is required.")
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        if errors is not None:
            errors.append(f"{field.replace('_', ' ').capitalize()} is not a valid date.")
        return None


def _details_from_form(learner_id=None):
    errors = []
    v = {
        "first_name": request.form.get("first_name", "").strip(),
        "last_name": request.form.get("last_name", "").strip(),
        "uln": request.form.get("uln", "").strip() or None,
        "email": request.form.get("email", "").strip().lower() or None,
        "phone": request.form.get("phone", "").strip() or None,
        "employer_name": request.form.get("employer_name", "").strip() or None,
        "employer_contact": request.form.get("employer_contact", "").strip() or None,
        "start_date": _date("start_date", True, errors),
        "planned_end_date": _date("planned_end_date", False, errors),
        "status": request.form.get("status", LearnerStatus.ACTIVE),
    }
    if not v["first_name"] or not v["last_name"]:
        errors.append("First and last name are required.")
    if v["uln"]:
        if not re.fullmatch(r"\d{10}", v["uln"]):
            errors.append("ULN must be 10 digits.")
        elif Learner.query.filter(Learner.uln == v["uln"], Learner.id != (learner_id or 0)).first():
            errors.append("Another learner already has that ULN.")
    if v["status"] not in LearnerStatus.LABELS:
        errors.append("Invalid status.")
    return errors, v


def _cohorts():
    return Cohort.query.filter_by(active=True).order_by(Cohort.name).all()


def _tutors():
    return User.query.filter_by(role=Role.TUTOR, active=True).order_by(User.name).all()


@bp.route("/")
@login_required
def list_learners():
    q = Learner.query.join(Cohort)
    if current_user.role == Role.TUTOR:
        q = q.filter(or_(Learner.tutor_id == current_user.id, Cohort.tutor_id == current_user.id))
    show = request.args.get("show", "current")
    if show == "archived":
        q = q.filter(Learner.archived_at.isnot(None))
    elif show != "all":
        q = q.filter(Learner.archived_at.is_(None))
    search = request.args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Learner.first_name.ilike(like), Learner.last_name.ilike(like),
                         Learner.uln.ilike(like), Learner.email.ilike(like)))
    for arg, col in (("cohort_id", Learner.cohort_id), ("tutor_id", Learner.tutor_id), ("course_id", Cohort.course_id)):
        value = request.args.get(arg, type=int)
        if value:
            q = q.filter(col == value)
    learners = q.order_by(Learner.last_name, Learner.first_name).limit(1000).all()
    return render_template("learners/list.html", learners=learners, show=show, search=search,
                           cohorts=Cohort.query.order_by(Cohort.name).all(), tutors=_tutors(),
                           courses=Course.query.order_by(Course.name).all())


@bp.route("/new", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def new():
    if request.method == "POST":
        errors, v = _details_from_form()
        cohort = db.session.get(Cohort, request.form.get("cohort_id", type=int) or 0)
        tutor_id = request.form.get("tutor_id", type=int)
        if cohort is None:
            errors.append("Choose a cohort.")
        tutor = db.session.get(User, tutor_id) if tutor_id else (cohort.tutor if cohort else None)
        if tutor is not None and tutor.role != Role.TUTOR:
            errors.append("Assigned tutor must have the Tutor role.")
        if not errors:
            learner = Learner(**v, cohort=cohort, tutor_id=tutor.id if tutor else None)
            db.session.add(learner)
            db.session.flush()
            placed_from = datetime.combine(v["start_date"], datetime.min.time())
            place_learner(learner, tutor, cohort, placed_from, "Enrolled", current_user)
            audit("learner.created", learner, f"Enrolled {learner.full_name} on {cohort.name}",
                  {"tutor": tutor.email if tutor else None, "start_date": v["start_date"]})
            db.session.commit()
            flash("Learner added.", "success")
            return redirect(url_for("learners.detail", learner_id=learner.id))
        for e in errors:
            flash(e, "error")
    return render_template("learners/form.html", learner=None, cohorts=_cohorts(), tutors=_tutors(),
                           statuses=LearnerStatus.LABELS, preset_cohort=request.args.get("cohort_id", type=int))


@bp.route("/<int:learner_id>")
@login_required
def detail(learner_id):
    learner = db.get_or_404(Learner, learner_id)
    if not can_view_learner(current_user, learner):
        abort(403)
    marks = (
        Attendance.query.join(TrainingSession).filter(Attendance.learner_id == learner.id)
        .order_by(TrainingSession.start_at.desc()).all()
    )
    tally = Tally()
    for m in marks:
        tally.add(m.status)
    alerts = PastoralAlert.query.filter_by(learner_id=learner.id).order_by(PastoralAlert.created_at.desc()).all()
    history = AuditLog.query.filter_by(entity_type="learners", entity_id=learner.id).order_by(AuditLog.id.desc()).all()
    return render_template("learners/detail.html", learner=learner, marks=marks, tally=tally, alerts=alerts,
                           history=history)


@bp.route("/<int:learner_id>/edit", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def edit(learner_id):
    learner = db.get_or_404(Learner, learner_id)
    if request.method == "POST":
        errors, v = _details_from_form(learner.id)
        if not errors:
            changes = diff(learner, EDITABLE, v)
            if "start_date" in changes and len(learner.assignments) == 1:
                # Keep the enrolment placement aligned with a corrected start date.
                learner.assignments[0].assigned_at = datetime.combine(v["start_date"], datetime.min.time())
            if changes:
                audit("learner.updated", learner, f"Updated details for {learner.full_name}", changes)
                db.session.commit()
            flash("Learner updated.", "success")
            return redirect(url_for("learners.detail", learner_id=learner.id))
        for e in errors:
            flash(e, "error")
    return render_template("learners/form.html", learner=learner, cohorts=_cohorts(), tutors=_tutors(),
                           statuses=LearnerStatus.LABELS, preset_cohort=None)


@bp.route("/<int:learner_id>/reassign", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def reassign(learner_id):
    learner = db.get_or_404(Learner, learner_id)
    if learner.is_archived:
        flash("Restore the learner before reassigning them.", "error")
        return redirect(url_for("learners.detail", learner_id=learner.id))
    if request.method == "POST":
        errors = []
        tutor = db.session.get(User, request.form.get("tutor_id", type=int) or 0)
        cohort = db.session.get(Cohort, request.form.get("cohort_id", type=int) or 0)
        reason = request.form.get("reason", "").strip()
        effective = _date("effective_date", True, errors)
        if tutor is None or tutor.role != Role.TUTOR:
            errors.append("Choose the new tutor.")
        if cohort is None:
            errors.append("Choose the cohort.")
        if not reason:
            errors.append("A reason is required – it forms part of the audit trail.")
        if tutor and cohort and tutor.id == learner.tutor_id and cohort.id == learner.cohort_id:
            errors.append("That is the learner's current tutor and cohort.")
        current = learner.current_assignment
        if effective and current:
            effective_at = datetime.combine(effective, datetime.min.time())
            if effective_at < current.assigned_at:
                errors.append("The effective date cannot be before the current placement started "
                              f"({current.assigned_at:%d/%m/%Y}).")
        if not errors:
            effective_at = datetime.combine(effective, datetime.min.time())
            if effective == today():
                effective_at = now()
            reassign_learner(learner, tutor, cohort, effective_at, reason, current_user)
            db.session.commit()
            flash(f"{learner.full_name} reassigned to {tutor.name}.", "success")
            return redirect(url_for("learners.detail", learner_id=learner.id))
        for e in errors:
            flash(e, "error")
    return render_template("learners/reassign.html", learner=learner, cohorts=_cohorts(), tutors=_tutors())


@bp.route("/<int:learner_id>/archive", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def archive(learner_id):
    learner = db.get_or_404(Learner, learner_id)
    if learner.is_archived:
        flash("Learner is already archived.", "info")
        return redirect(url_for("learners.detail", learner_id=learner.id))
    if request.method == "POST":
        errors = []
        leave_date = _date("leave_date", True, errors)
        reason = request.form.get("leave_reason")
        notes = request.form.get("leave_notes", "").strip()
        if reason not in LeaveReason.LABELS:
            errors.append("Choose a reason for leaving.")
        if not errors:
            learner.archived_at = now()
            learner.archived_by_id = current_user.id
            learner.leave_date = leave_date
            learner.leave_reason = reason
            learner.leave_notes = notes or None
            current = learner.current_assignment
            if current:
                current.ended_at = datetime.combine(leave_date, datetime.max.time()).replace(microsecond=0)
            audit("learner.archived", learner, f"Archived {learner.full_name} – {LeaveReason.LABELS[reason]}",
                  {"leave_date": leave_date, "reason": reason, "notes": notes})
            db.session.commit()
            flash(f"{learner.full_name} archived. Their records are retained and remain reportable.", "success")
            return redirect(url_for("learners.detail", learner_id=learner.id))
        for e in errors:
            flash(e, "error")
    return render_template("learners/archive.html", learner=learner, reasons=LeaveReason.LABELS)


@bp.route("/<int:learner_id>/restore", methods=["POST"])
@roles_required(Role.ADMIN)
def restore(learner_id):
    learner = db.get_or_404(Learner, learner_id)
    reason = request.form.get("reason", "").strip()
    if not learner.is_archived:
        abort(400)
    if not reason:
        flash("A reason is required to restore a learner.", "error")
        return redirect(url_for("learners.detail", learner_id=learner.id))
    details = {"previous_leave_date": learner.leave_date, "previous_reason": learner.leave_reason, "reason": reason}
    learner.archived_at = None
    learner.archived_by_id = None
    learner.leave_date = None
    learner.leave_reason = None
    learner.leave_notes = None
    reassign_learner(learner, learner.tutor, learner.cohort, now(), f"Restored from archive: {reason}", current_user)
    audit("learner.restored", learner, f"Restored {learner.full_name} from archive", details)
    db.session.commit()
    flash("Learner restored.", "success")
    return redirect(url_for("learners.detail", learner_id=learner.id))
