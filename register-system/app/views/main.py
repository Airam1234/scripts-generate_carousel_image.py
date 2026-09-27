from datetime import datetime, timedelta

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..models import AlertStatus, Cohort, Learner, PastoralAlert, Role, TrainingSession, User
from ..reports import month_summary
from ..timeutil import now

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def dashboard():
    if current_user.role == Role.PASTORAL:
        return redirect(url_for("pastoral.alerts"))
    if current_user.role == Role.INSPECTOR:
        return render_template("inspector_dashboard.html")

    t = now()
    day_start = datetime(t.year, t.month, t.day)
    day_end = day_start + timedelta(days=1)

    sessions_q = TrainingSession.query.filter(TrainingSession.cancelled_at.is_(None))
    if current_user.role == Role.TUTOR:
        sessions_q = sessions_q.filter(TrainingSession.tutor_id == current_user.id)

    todays = sessions_q.filter(
        TrainingSession.start_at >= day_start, TrainingSession.start_at < day_end
    ).order_by(TrainingSession.start_at).all()
    upcoming = sessions_q.filter(
        TrainingSession.start_at >= day_end, TrainingSession.start_at < day_end + timedelta(days=14)
    ).order_by(TrainingSession.start_at).all()
    outstanding = sessions_q.filter(
        TrainingSession.start_at < t, TrainingSession.register_completed_at.is_(None)
    ).order_by(TrainingSession.start_at.desc()).limit(50).all()

    summary = month_summary(t.year, t.month, tutor_id=current_user.id if current_user.role == Role.TUTOR else None)

    ctx = dict(todays=todays, upcoming=upcoming, outstanding=outstanding, summary=summary)
    if current_user.role == Role.TUTOR:
        ctx["cohorts"] = Cohort.query.filter_by(tutor_id=current_user.id, active=True).order_by(Cohort.name).all()
        ctx["learner_count"] = Learner.query.filter_by(tutor_id=current_user.id, archived_at=None).count()
        return render_template("tutor_dashboard.html", **ctx)

    ctx.update(
        open_alerts=PastoralAlert.query.filter(PastoralAlert.status != AlertStatus.CLOSED).count(),
        learner_count=Learner.query.filter_by(archived_at=None).count(),
        cohort_count=Cohort.query.filter_by(active=True).count(),
        tutor_count=User.query.filter_by(role=Role.TUTOR, active=True).count(),
    )
    return render_template("admin_dashboard.html", **ctx)
