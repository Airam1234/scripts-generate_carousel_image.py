from datetime import date, datetime, timedelta

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..audit import audit, diff
from ..extensions import db
from ..models import (
    Attendance,
    AttendanceStatus,
    Cohort,
    DeliveryMode,
    PastoralAlert,
    Role,
    SessionType,
    TrainingSession,
    User,
)
from ..notifications import notify_pastoral, process_due_sessions, reconcile_alert_after_mark
from ..security import can_mark_session, can_view_session, roles_required
from ..timeutil import (
    add_months,
    is_first_day_window,
    is_monthly_window,
    minutes_between,
    month_bounds,
    now,
    parse_month,
    weekday_in_first_week,
)

bp = Blueprint("sessions", __name__, url_prefix="/sessions")

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def schedule_problem(session_type, day):
    if session_type == SessionType.FIRST_DAY and not is_first_day_window(day):
        return "First day of learning sessions must be in week 3 or 4 of the month (15th–28th)."
    if session_type == SessionType.MONTHLY and not is_monthly_window(day):
        return "Monthly sessions must be in the first week of the month (1st–7th)."
    return None


def _cohorts_for_user():
    q = Cohort.query.filter_by(active=True)
    if current_user.role == Role.TUTOR:
        q = q.filter_by(tutor_id=current_user.id)
    return q.order_by(Cohort.name).all()


def _tutors():
    return User.query.filter_by(role=Role.TUTOR, active=True).order_by(User.name).all()


@bp.route("/")
@login_required
def list_sessions():
    year, month = parse_month(request.args.get("month"))
    start, end = month_bounds(year, month)
    q = TrainingSession.query.filter(TrainingSession.start_at >= start, TrainingSession.start_at < end)
    if current_user.role == Role.TUTOR:
        q = q.filter(TrainingSession.tutor_id == current_user.id)
    for arg, col in (("cohort_id", TrainingSession.cohort_id), ("tutor_id", TrainingSession.tutor_id)):
        value = request.args.get(arg, type=int)
        if value:
            q = q.filter(col == value)
    stype = request.args.get("type")
    if stype in SessionType.LABELS:
        q = q.filter(TrainingSession.session_type == stype)
    sessions = q.order_by(TrainingSession.start_at).all()
    py, pm = add_months(year, month, -1)
    ny, nm = add_months(year, month, 1)
    return render_template(
        "sessions/list.html", sessions=sessions, year=year, month=month,
        month_value=f"{year:04d}-{month:02d}", prev_month=f"{py:04d}-{pm:02d}", next_month=f"{ny:04d}-{nm:02d}",
        cohorts=_cohorts_for_user(), tutors=_tutors(), stype=stype,
    )


def _session_form(existing=None):
    """Validate the session form; returns (errors, values)."""
    errors = []
    cohort = db.session.get(Cohort, request.form.get("cohort_id", type=int) or 0)
    if cohort is None or (current_user.role == Role.TUTOR and cohort.tutor_id != current_user.id):
        errors.append("Choose one of your cohorts.")
    stype = request.form.get("session_type")
    if stype not in SessionType.LABELS:
        errors.append("Choose a session type.")
    try:
        start_at = datetime.strptime(
            f"{request.form.get('date', '')} {request.form.get('time', '')}", "%Y-%m-%d %H:%M"
        )
    except ValueError:
        start_at = None
        errors.append("Enter a valid date and start time.")
    duration = request.form.get("duration_minutes", type=int)
    if not duration or not 15 <= duration <= 600:
        errors.append("Duration must be between 15 and 600 minutes.")
    mode = request.form.get("delivery_mode", "online")
    if mode not in DeliveryMode.LABELS:
        errors.append("Choose a delivery mode.")
    tutor = cohort.tutor if cohort else None
    if current_user.role == Role.ADMIN and request.form.get("tutor_id", type=int):
        tutor = db.session.get(User, request.form.get("tutor_id", type=int))
        if tutor is None or tutor.role != Role.TUTOR:
            errors.append("Choose a valid tutor.")
    title = request.form.get("title", "").strip()
    if not title and cohort and stype in SessionType.LABELS:
        title = f"{cohort.name} – {SessionType.LABELS[stype]}"

    override = None
    if start_at and stype:
        problem = schedule_problem(stype, start_at.date())
        if problem:
            override = request.form.get("override_reason", "").strip()
            if current_user.role != Role.ADMIN:
                errors.append(problem + " Ask an administrator if this session needs to run outside the window.")
            elif not override:
                errors.append(problem + " To schedule it anyway, give an override reason.")
    if start_at and current_user.role != Role.ADMIN and start_at < now() and existing is None:
        errors.append("Tutors cannot create sessions in the past – ask an administrator.")
    return errors, {
        "cohort": cohort, "session_type": stype, "start_at": start_at, "duration_minutes": duration,
        "delivery_mode": mode, "location": request.form.get("location", "").strip() or None,
        "title": title[:160], "tutor": tutor, "schedule_override_reason": override or None,
    }


def _mark_retrospective(s):
    grace = timedelta(minutes=current_app.config["PASTORAL_GRACE_MINUTES"])
    if s.start_at + grace <= now() and s.pastoral_processed_at is None:
        # Session entered after the fact: record it but don't send same-day pastoral alerts.
        s.pastoral_processed_at = now()
        return True
    return False


@bp.route("/new", methods=["GET", "POST"])
@roles_required(Role.ADMIN, Role.TUTOR)
def new():
    if request.method == "POST":
        errors, v = _session_form()
        if not errors:
            s = TrainingSession(
                cohort=v["cohort"], tutor=v["tutor"], session_type=v["session_type"], title=v["title"],
                start_at=v["start_at"], duration_minutes=v["duration_minutes"], delivery_mode=v["delivery_mode"],
                location=v["location"], schedule_override_reason=v["schedule_override_reason"],
                created_by_id=current_user.id,
            )
            db.session.add(s)
            db.session.flush()
            retro = _mark_retrospective(s)
            audit("session.created", s, f"Scheduled {s.title} on {s.start_at:%d/%m/%Y %H:%M}", {
                "type": s.session_type, "tutor": s.tutor.email if s.tutor else None,
                "override_reason": s.schedule_override_reason, "retrospective": retro,
            })
            db.session.commit()
            flash("Session scheduled." + (" It is in the past, so no automatic pastoral alerts will be sent."
                                          if retro else ""), "success")
            return redirect(url_for("sessions.register", session_id=s.id))
        for e in errors:
            flash(e, "error")
    return render_template("sessions/form.html", s=None, cohorts=_cohorts_for_user(), tutors=_tutors(),
                           modes=DeliveryMode.LABELS, preset_cohort=request.args.get("cohort_id", type=int))


@bp.route("/<int:session_id>/edit", methods=["GET", "POST"])
@login_required
def edit(session_id):
    s = db.get_or_404(TrainingSession, session_id)
    if not can_mark_session(current_user, s):
        abort(403)
    if current_user.role != Role.ADMIN and s.start_at <= now():
        flash("Sessions that have started can only be changed by an administrator.", "error")
        return redirect(url_for("sessions.register", session_id=s.id))
    if request.method == "POST":
        errors, v = _session_form(existing=s)
        if not errors:
            values = {k: v[k] for k in ("session_type", "start_at", "duration_minutes", "delivery_mode",
                                        "location", "title", "schedule_override_reason")}
            values["cohort_id"] = v["cohort"].id
            values["tutor_id"] = v["tutor"].id if v["tutor"] else None
            changes = diff(s, list(values), values)
            if "start_at" in changes and s.start_at > now():
                s.pastoral_processed_at = None  # rescheduled into the future: re-arm the 15-minute check
            _mark_retrospective(s)
            if changes:
                audit("session.updated", s, f"Updated {s.title}", changes)
                db.session.commit()
            flash("Session updated.", "success")
            return redirect(url_for("sessions.register", session_id=s.id))
        for e in errors:
            flash(e, "error")
    return render_template("sessions/form.html", s=s, cohorts=_cohorts_for_user(), tutors=_tutors(),
                           modes=DeliveryMode.LABELS, preset_cohort=None)


@bp.route("/<int:session_id>/cancel", methods=["POST"])
@login_required
def cancel(session_id):
    s = db.get_or_404(TrainingSession, session_id)
    if not can_mark_session(current_user, s):
        abort(403)
    reason = request.form.get("cancel_reason", "").strip()
    if s.is_cancelled:
        flash("Session is already cancelled.", "info")
    elif not reason:
        flash("A reason is required to cancel a session.", "error")
    elif Attendance.query.filter_by(session_id=s.id, auto_recorded=False).count() and current_user.role != Role.ADMIN:
        flash("Attendance has already been taken – ask an administrator to cancel this session.", "error")
    else:
        s.cancelled_at = now()
        s.cancel_reason = reason
        audit("session.cancelled", s, f"Cancelled {s.title}", {"reason": reason})
        db.session.commit()
        flash("Session cancelled. It will be shown as cancelled in reports.", "success")
    return redirect(url_for("sessions.register", session_id=s.id))


@bp.route("/bulk-monthly", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def bulk_monthly():
    """Schedule a cohort's monthly sessions on a fixed weekday in the first week of each month."""
    if request.method == "POST":
        errors = []
        cohort = db.session.get(Cohort, request.form.get("cohort_id", type=int) or 0)
        weekday = request.form.get("weekday", type=int)
        months = request.form.get("months", type=int)
        duration = request.form.get("duration_minutes", type=int)
        year, month = parse_month(request.form.get("from_month"), default=(0, 0))
        try:
            start_time = datetime.strptime(request.form.get("time", ""), "%H:%M").time()
        except ValueError:
            start_time = None
        if cohort is None:
            errors.append("Choose a cohort.")
        if weekday is None or not 0 <= weekday <= 6:
            errors.append("Choose a weekday.")
        if not months or not 1 <= months <= 36:
            errors.append("Number of months must be 1–36.")
        if not duration or not 15 <= duration <= 600:
            errors.append("Duration must be 15–600 minutes.")
        if not year or start_time is None:
            errors.append("Enter a valid first month and start time.")
        if not errors:
            created, skipped = 0, 0
            for i in range(months):
                y, m = add_months(year, month, i)
                day = weekday_in_first_week(y, m, weekday)
                start_at = datetime.combine(day, start_time)
                m_start, m_end = month_bounds(y, m)
                exists = TrainingSession.query.filter(
                    TrainingSession.cohort_id == cohort.id,
                    TrainingSession.session_type == SessionType.MONTHLY,
                    TrainingSession.start_at >= m_start, TrainingSession.start_at < m_end,
                    TrainingSession.cancelled_at.is_(None),
                ).first()
                if exists or start_at < now():
                    skipped += 1
                    continue
                s = TrainingSession(
                    cohort=cohort, tutor_id=cohort.tutor_id, session_type=SessionType.MONTHLY,
                    title=f"{cohort.name} – Monthly session ({day:%B %Y})", start_at=start_at,
                    duration_minutes=duration, delivery_mode=request.form.get("delivery_mode", "online"),
                    location=request.form.get("location", "").strip() or None, created_by_id=current_user.id,
                )
                db.session.add(s)
                created += 1
            audit("session.bulk_created", cohort, f"Scheduled {created} monthly sessions for {cohort.name}",
                  {"weekday": WEEKDAYS[weekday], "time": start_time, "months": months, "skipped": skipped})
            db.session.commit()
            flash(f"{created} monthly session(s) created, {skipped} skipped (already scheduled or in the past).",
                  "success")
            return redirect(url_for("cohorts.detail", cohort_id=cohort.id))
        for e in errors:
            flash(e, "error")
    return render_template("sessions/bulk_monthly.html", cohorts=_cohorts_for_user(), weekdays=WEEKDAYS,
                           modes=DeliveryMode.LABELS, today=date.today())


# ---- the register ---------------------------------------------------------------

def _register_state(s):
    cfg = current_app.config
    t = now()
    opens = s.start_at - timedelta(minutes=cfg["REGISTER_OPENS_MINUTES_BEFORE"])
    closes = s.start_at + timedelta(days=cfg["TUTOR_EDIT_WINDOW_DAYS"])
    reason = None
    if s.is_cancelled:
        reason = "This session was cancelled."
    elif not can_mark_session(current_user, s):
        reason = "Read-only: only the session's tutor or an administrator can mark this register."
    elif t < opens:
        reason = f"The register opens at {opens:%H:%M on %d/%m/%Y}."
    elif current_user.role != Role.ADMIN and t > closes:
        reason = (f"The tutor editing window closed on {closes:%d/%m/%Y}. "
                  "Ask an administrator to amend this register.")
    return {
        "editable": reason is None,
        # Edit/cancel the session itself: admins any time, the tutor until it starts.
        "can_manage": not s.is_cancelled and can_mark_session(current_user, s)
        and (current_user.role == Role.ADMIN or s.start_at > t),
        "locked_reason": reason,
        "alert_due_at": s.start_at + timedelta(minutes=cfg["PASTORAL_GRACE_MINUTES"]),
        "minutes_since_start": minutes_between(s.start_at, t),
    }


@bp.route("/<int:session_id>/register", methods=["GET", "POST"])
@login_required
def register(session_id):
    s = db.get_or_404(TrainingSession, session_id)
    if not can_view_session(current_user, s):
        abort(403)
    state = _register_state(s)
    learners = s.expected_learners()
    marks = {a.learner_id: a for a in Attendance.query.filter_by(session_id=s.id)}

    if request.method == "POST":
        if not state["editable"]:
            abort(403)
        amend_reason = request.form.get("amend_reason", "").strip()
        pending, errors = [], []
        for learner in learners:
            status = request.form.get(f"status_{learner.id}", "")
            if not status:
                continue
            if status not in AttendanceStatus.LABELS:
                abort(400)
            minutes_late = request.form.get(f"late_{learner.id}", type=int) if status == AttendanceStatus.LATE else None
            if minutes_late is not None and not 0 <= minutes_late <= s.duration_minutes:
                errors.append(f"Minutes late for {learner.full_name} is out of range.")
            note = request.form.get(f"note_{learner.id}", "").strip()[:500] or None
            pending.append((learner, status, minutes_late, note))

        existing_changes = [
            p for p in pending
            if p[0].id in marks and not marks[p[0].id].auto_recorded
            and (marks[p[0].id].status, marks[p[0].id].minutes_late, marks[p[0].id].note) != p[1:]
        ]
        if existing_changes and s.register_completed_at and not amend_reason:
            errors.append("You are changing a submitted register – give a reason for the amendment.")
        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(url_for("sessions.register", session_id=s.id))

        new_alerts = []
        t = now()
        for learner, status, minutes_late, note in pending:
            att = marks.get(learner.id)
            if att is None:
                att = Attendance(session_id=s.id, learner_id=learner.id, status=status, minutes_late=minutes_late,
                                 note=note, marked_by_id=current_user.id, marked_at=t)
                db.session.add(att)
                marks[learner.id] = att
                audit("attendance.marked", s, f"{learner.full_name}: {AttendanceStatus.LABELS[status]}",
                      {"learner_id": learner.id, "status": status, "minutes_late": minutes_late, "note": note})
            elif (att.status, att.minutes_late, att.note) != (status, minutes_late, note) or att.auto_recorded:
                old = {"status": att.status, "minutes_late": att.minutes_late, "note": att.note,
                       "auto_recorded": att.auto_recorded, "marked_by": att.marked_by_id}
                att.status, att.minutes_late, att.note = status, minutes_late, note
                att.auto_recorded = False
                att.marked_by_id = current_user.id
                att.marked_at = t
                audit("attendance.amended", s,
                      f"{learner.full_name}: {AttendanceStatus.LABELS.get(old['status'])} → "
                      f"{AttendanceStatus.LABELS[status]}",
                      {"learner_id": learner.id, "from": old, "to": status, "minutes_late": minutes_late,
                       "reason": amend_reason or None})
            else:
                continue
            alert = reconcile_alert_after_mark(s, learner, status, current_user)
            if alert is not None:
                new_alerts.append(alert)

        if s.register_completed_at is None and learners and all(l.id in marks for l in learners):
            s.register_completed_at = t
            audit("register.completed", s, f"Register completed for {s.title}",
                  {"minutes_after_start": minutes_between(s.start_at, t)})
        db.session.commit()
        if new_alerts:
            notify_pastoral(s, new_alerts)
        process_due_sessions()
        flash("Register saved." if s.register_completed_at else
              "Register saved – some learners are still unmarked.", "success")
        return redirect(url_for("sessions.register", session_id=s.id))

    alerts = {a.learner_id: a for a in PastoralAlert.query.filter_by(session_id=s.id)}
    return render_template("sessions/register.html", s=s, learners=learners, marks=marks, alerts=alerts,
                           state=state, statuses=AttendanceStatus.LABELS)
