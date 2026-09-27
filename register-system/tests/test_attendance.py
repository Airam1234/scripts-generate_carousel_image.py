from datetime import datetime

from app.extensions import db
from app.models import (
    AlertStatus,
    Attendance,
    AuditLog,
    EmailLog,
    PastoralAlert,
    SessionType,
    TrainingSession,
)
from app.notifications import process_due_sessions

from .conftest import freeze, login


def make_session(cohort, start):
    s = TrainingSession(cohort=cohort, tutor=cohort.tutor, session_type=SessionType.MONTHLY,
                        title="Monthly", start_at=start, duration_minutes=180)
    db.session.add(s)
    db.session.commit()
    return s


def test_register_marks_and_pastoral_alert_after_15_minutes(client, people, cohort, monkeypatch):
    start = datetime(2026, 10, 6, 10, 0)
    s = make_session(cohort, start)
    ann, ben, cat = cohort.test_learners

    freeze(monkeypatch, datetime(2026, 10, 6, 10, 5))
    login(client, "tutor@x.org")
    r = client.post(f"/sessions/{s.id}/register", data={f"status_{ann.id}": "present", f"status_{ben.id}": "absent"})
    assert r.status_code == 302
    assert PastoralAlert.query.count() == 0  # not yet 15 minutes

    freeze(monkeypatch, datetime(2026, 10, 6, 10, 14))
    assert process_due_sessions() == 0

    freeze(monkeypatch, datetime(2026, 10, 6, 10, 15))
    assert process_due_sessions() == 1
    alerts = {a.learner_id: a for a in PastoralAlert.query}
    assert set(alerts) == {ben.id, cat.id}  # absent + never marked
    cat_mark = Attendance.query.filter_by(session_id=s.id, learner_id=cat.id).one()
    assert cat_mark.auto_recorded and cat_mark.status == "absent"
    email = EmailLog.query.one()
    assert f"/pastoral/session/{s.id}" in email.body
    assert "Ben" not in email.body  # no learner names in email
    assert process_due_sessions() == 0  # only once

    # Cat arrives late: tutor updates, alert closes automatically.
    freeze(monkeypatch, datetime(2026, 10, 6, 10, 25))
    client.post(f"/sessions/{s.id}/register", data={f"status_{ann.id}": "present", f"status_{ben.id}": "absent",
                                                   f"status_{cat.id}": "late", f"late_{cat.id}": "25"})
    db.session.expire_all()
    cat_alert = PastoralAlert.query.filter_by(learner_id=cat.id).one()
    assert cat_alert.status == AlertStatus.CLOSED and cat_alert.outcome == "attended"
    assert db.session.get(TrainingSession, s.id).register_completed_at is not None


def test_amending_submitted_register_needs_reason_and_is_audited(client, people, cohort, monkeypatch):
    s = make_session(cohort, datetime(2026, 10, 6, 10, 0))
    ann, ben, cat = cohort.test_learners
    freeze(monkeypatch, datetime(2026, 10, 6, 10, 5))
    login(client, "tutor@x.org")
    data = {f"status_{l.id}": "present" for l in cohort.test_learners}
    client.post(f"/sessions/{s.id}/register", data=data)
    data[f"status_{ben.id}"] = "absent"
    client.post(f"/sessions/{s.id}/register", data=data)
    assert Attendance.query.filter_by(learner_id=ben.id).one().status == "present"  # rejected
    data["amend_reason"] = "Marked in error"
    client.post(f"/sessions/{s.id}/register", data=data)
    assert Attendance.query.filter_by(learner_id=ben.id).one().status == "absent"
    entry = AuditLog.query.filter_by(action="attendance.amended").one()
    assert entry.details_dict["reason"] == "Marked in error"


def test_other_tutor_cannot_mark(client, people, cohort, monkeypatch):
    s = make_session(cohort, datetime(2026, 10, 6, 10, 0))
    freeze(monkeypatch, datetime(2026, 10, 6, 10, 5))
    login(client, "tutor2@x.org")
    assert client.post(f"/sessions/{s.id}/register", data={}).status_code == 403


def test_register_locked_for_tutor_after_window(client, people, cohort, monkeypatch):
    s = make_session(cohort, datetime(2026, 10, 6, 10, 0))
    freeze(monkeypatch, datetime(2026, 10, 20, 10, 0))
    login(client, "tutor@x.org")
    assert client.post(f"/sessions/{s.id}/register", data={}).status_code == 403


def test_tutor_cannot_schedule_monthly_outside_first_week(client, people, cohort, monkeypatch):
    freeze(monkeypatch, datetime(2026, 9, 27, 9, 0))
    login(client, "tutor@x.org")
    client.post("/sessions/new", data={"cohort_id": cohort.id, "session_type": "monthly", "date": "2026-10-14",
                                       "time": "10:00", "duration_minutes": "180", "delivery_mode": "online"})
    assert TrainingSession.query.count() == 0
    client.post("/sessions/new", data={"cohort_id": cohort.id, "session_type": "monthly", "date": "2026-10-06",
                                       "time": "10:00", "duration_minutes": "180", "delivery_mode": "online"})
    assert TrainingSession.query.count() == 1


def test_admin_override_is_recorded(client, people, cohort, monkeypatch):
    freeze(monkeypatch, datetime(2026, 9, 27, 9, 0))
    login(client, "admin@x.org")
    client.post("/sessions/new", data={"cohort_id": cohort.id, "session_type": "monthly", "date": "2026-10-14",
                                       "time": "10:00", "duration_minutes": "180", "delivery_mode": "online",
                                       "override_reason": "Half term"})
    assert TrainingSession.query.one().schedule_override_reason == "Half term"


def test_bulk_monthly(client, people, cohort, monkeypatch):
    freeze(monkeypatch, datetime(2026, 9, 27, 9, 0))
    login(client, "admin@x.org")
    client.post("/sessions/bulk-monthly", data={"cohort_id": cohort.id, "weekday": "1", "time": "10:00",
                                                "from_month": "2026-10", "months": "6", "duration_minutes": "180"})
    sessions = TrainingSession.query.all()
    assert len(sessions) == 6
    assert all(s.start_at.day <= 7 and s.start_at.weekday() == 1 for s in sessions)
