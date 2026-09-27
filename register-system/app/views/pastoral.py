from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..audit import audit
from ..extensions import db
from ..models import (
    AlertOutcome,
    AlertStatus,
    Attendance,
    ContactMethod,
    PastoralAlert,
    PastoralContact,
    Role,
    TrainingSession,
)
from ..security import roles_required
from ..timeutil import now

bp = Blueprint("pastoral", __name__, url_prefix="/pastoral")

VIEWERS = (Role.ADMIN, Role.PASTORAL, Role.INSPECTOR)


@bp.route("/")
@roles_required(*VIEWERS)
def alerts():
    show = request.args.get("show", "open")
    q = PastoralAlert.query.join(TrainingSession)
    if show == "open":
        q = q.filter(PastoralAlert.status != AlertStatus.CLOSED)
    elif show == "closed":
        q = q.filter(PastoralAlert.status == AlertStatus.CLOSED)
    items = q.order_by(TrainingSession.start_at.desc(), PastoralAlert.id).limit(500).all()
    return render_template("pastoral/alerts.html", alerts=items, show=show)


@bp.route("/session/<int:session_id>")
@roles_required(*VIEWERS)
def session_alerts(session_id):
    """Landing page for the link emailed to Pastoral Support."""
    s = db.get_or_404(TrainingSession, session_id)
    items = PastoralAlert.query.filter_by(session_id=s.id).order_by(PastoralAlert.id).all()
    return render_template("pastoral/session.html", s=s, alerts=items)


@bp.route("/alert/<int:alert_id>", methods=["GET", "POST"])
@roles_required(*VIEWERS)
def alert(alert_id):
    a = db.get_or_404(PastoralAlert, alert_id)
    if request.method == "POST":
        if current_user.role not in (Role.ADMIN, Role.PASTORAL):
            abort(403)
        method = request.form.get("method")
        outcome = request.form.get("outcome") or None
        notes = request.form.get("notes", "").strip()
        close = request.form.get("close") == "on"
        if method not in ContactMethod.LABELS:
            flash("Choose how you contacted (or tried to contact) the learner.", "error")
        elif outcome and outcome not in AlertOutcome.LABELS:
            abort(400)
        elif close and not outcome:
            flash("Choose an outcome before closing the alert.", "error")
        elif not notes:
            flash("Add a note describing the contact.", "error")
        else:
            db.session.add(PastoralContact(alert=a, user_id=current_user.id, method=method, outcome=outcome,
                                           notes=notes, contacted_at=now()))
            if outcome:
                a.outcome = outcome
            if close:
                a.status = AlertStatus.CLOSED
                a.closed_at = now()
                a.closed_by_id = current_user.id
            elif a.status == AlertStatus.OPEN:
                a.status = AlertStatus.IN_PROGRESS
            audit("pastoral.contact_logged", a.learner,
                  f"Pastoral contact ({ContactMethod.LABELS[method]}) for {a.learner.full_name}",
                  {"alert_id": a.id, "session_id": a.session_id, "outcome": outcome, "closed": close})
            db.session.commit()
            flash("Contact logged.", "success")
            return redirect(url_for("pastoral.session_alerts", session_id=a.session_id))
    mark = Attendance.query.filter_by(session_id=a.session_id, learner_id=a.learner_id).first()
    return render_template("pastoral/alert.html", a=a, mark=mark, methods=ContactMethod.LABELS,
                           outcomes=AlertOutcome.LABELS)
