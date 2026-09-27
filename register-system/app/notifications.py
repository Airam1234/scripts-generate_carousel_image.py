"""Pastoral alerts: 15 minutes after a session starts, anyone not marked Present
or Late is flagged to Pastoral Support, who receive an email with a link to
the follow-up page for that session.
"""
import logging
import smtplib
from datetime import timedelta
from email.message import EmailMessage

from flask import current_app
from sqlalchemy import update

from .audit import audit
from .extensions import db
from .models import (
    AlertStatus,
    Attendance,
    AttendanceStatus,
    EmailLog,
    PastoralAlert,
    PastoralContact,
    Role,
    TrainingSession,
    User,
)
from .timeutil import now

log = logging.getLogger(__name__)


def pastoral_recipients():
    shared = current_app.config.get("PASTORAL_EMAIL")
    if shared:
        return [e.strip() for e in shared.split(",") if e.strip()]
    users = User.query.filter_by(role=Role.PASTORAL, active=True).all()
    return [u.email for u in users if u.is_active]


def send_email(recipients, subject, body):
    """Send via SMTP when configured. Every message is kept in EmailLog."""
    entry = EmailLog(recipients=", ".join(recipients), subject=subject, body=body)
    db.session.add(entry)
    cfg = current_app.config
    if not recipients:
        entry.error = "No pastoral recipients configured"
    elif not cfg.get("SMTP_HOST"):
        entry.error = "SMTP not configured – message logged only"
        log.info("EMAIL (not sent, SMTP not configured) to %s: %s\n%s", recipients, subject, body)
    else:
        msg = EmailMessage()
        msg["From"] = cfg["MAIL_FROM"]
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content(body)
        try:
            with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=20) as smtp:
                if cfg["SMTP_USE_TLS"]:
                    smtp.starttls()
                if cfg.get("SMTP_USERNAME"):
                    smtp.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
                smtp.send_message(msg)
            entry.sent = True
        except Exception as exc:  # noqa: BLE001 - never let email break a register
            entry.error = str(exc)[:1000]
            log.exception("Failed to send pastoral email")
    db.session.commit()
    return entry


def notify_pastoral(session, alerts):
    if not alerts:
        return None
    link = f"{current_app.config['BASE_URL']}/pastoral/session/{session.id}"
    # Keep personal data out of email: names are only visible after logging in.
    body = (
        f"{len(alerts)} learner(s) had not arrived {current_app.config['PASTORAL_GRACE_MINUTES']} "
        f"minutes after the start of a session and need a follow-up call.\n\n"
        f"Session: {session.title}\n"
        f"Cohort: {session.cohort.name} ({session.cohort.course.title})\n"
        f"Tutor: {session.tutor.name if session.tutor else 'Unassigned'}\n"
        f"Started: {session.start_at:%A %d %B %Y, %H:%M}\n\n"
        f"Open the follow-up list (login required):\n{link}\n"
    )
    subject = f"Attendance follow-up needed: {session.cohort.name} – {session.start_at:%d/%m %H:%M}"
    return send_email(pastoral_recipients(), subject, body)


def _raise_alert(session, learner_id):
    existing = PastoralAlert.query.filter_by(session_id=session.id, learner_id=learner_id).first()
    if existing:
        if existing.status == AlertStatus.CLOSED and existing.outcome == "attended":
            # Tutor changed a learner back to absent: reopen the follow-up.
            existing.status = AlertStatus.OPEN
            existing.outcome = None
            existing.closed_at = None
            existing.closed_by_id = None
            return existing
        return None
    alert = PastoralAlert(session_id=session.id, learner_id=learner_id)
    db.session.add(alert)
    return alert


def raise_alerts_for_session(session, at=None):
    """Create absence records for unmarked learners and alerts for every absentee."""
    at = at or now()
    marks = {a.learner_id: a for a in Attendance.query.filter_by(session_id=session.id)}
    alerts = []
    for learner in session.expected_learners():
        att = marks.get(learner.id)
        if att is None:
            att = Attendance(
                session_id=session.id,
                learner_id=learner.id,
                status=AttendanceStatus.ABSENT,
                auto_recorded=True,
                note="Not marked within the first 15 minutes – recorded absent by the system",
                marked_at=at,
            )
            db.session.add(att)
        if att.status == AttendanceStatus.ABSENT:
            alert = _raise_alert(session, learner.id)
            if alert is not None:
                alerts.append(alert)
    db.session.flush()
    if alerts:
        audit(
            "pastoral.alerts_raised",
            session,
            f"{len(alerts)} pastoral alert(s) raised for {session.title}",
            {"learner_ids": [a.learner_id for a in alerts]},
        )
    return alerts


def process_due_sessions(at=None):
    """Run the 15-minute check for every session that has reached it.

    Safe to call from several workers at once: each session is claimed with a
    conditional UPDATE so alerts are only ever raised once.
    """
    at = at or now()
    cutoff = at - timedelta(minutes=current_app.config["PASTORAL_GRACE_MINUTES"])
    due_ids = [
        sid
        for (sid,) in db.session.query(TrainingSession.id).filter(
            TrainingSession.start_at <= cutoff,
            TrainingSession.pastoral_processed_at.is_(None),
            TrainingSession.cancelled_at.is_(None),
        )
    ]
    processed = 0
    for sid in due_ids:
        claimed = db.session.execute(
            update(TrainingSession)
            .where(TrainingSession.id == sid, TrainingSession.pastoral_processed_at.is_(None))
            .values(pastoral_processed_at=at)
        ).rowcount
        if not claimed:
            db.session.rollback()
            continue
        session = db.session.get(TrainingSession, sid)
        alerts = raise_alerts_for_session(session, at)
        db.session.commit()
        notify_pastoral(session, alerts)
        processed += 1
    return processed


def reconcile_alert_after_mark(session, learner, new_status, user):
    """Keep alerts in step with register changes made after the 15-minute check.

    Returns a newly-raised alert (for learners changed to Absent) or None.
    """
    if session.pastoral_processed_at is None:
        return None
    alert = PastoralAlert.query.filter_by(session_id=session.id, learner_id=learner.id).first()
    if new_status in AttendanceStatus.ATTENDED or new_status == AttendanceStatus.AUTHORISED:
        if alert and alert.status != AlertStatus.CLOSED:
            alert.status = AlertStatus.CLOSED
            alert.outcome = "attended" if new_status in AttendanceStatus.ATTENDED else "reason_given"
            alert.closed_at = now()
            alert.closed_by_id = user.id
            db.session.add(PastoralContact(
                alert=alert,
                user_id=user.id,
                outcome=alert.outcome,
                notes=f"Register updated by {user.name} to "
                      f"'{AttendanceStatus.LABELS[new_status]}'. Alert closed automatically.",
            ))
        return None
    if new_status == AttendanceStatus.ABSENT:
        return _raise_alert(session, learner.id)
    return None

