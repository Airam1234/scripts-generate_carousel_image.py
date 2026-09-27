from datetime import datetime

from app.extensions import db
from app.models import Attendance, Learner, LearnerAssignment, SessionType, TrainingSession
from app.reports import month_summary

from .conftest import freeze, login


def test_reassign_keeps_history(client, people, cohort, monkeypatch):
    freeze(monkeypatch, datetime(2026, 10, 10, 9, 0))
    ann = cohort.test_learners[0]
    login(client, "admin@x.org")
    r = client.post(f"/learners/{ann.id}/reassign", data={"tutor_id": people["tutor2"].id, "cohort_id": cohort.id,
                                                           "effective_date": "2026-10-10", "reason": "Caseload"})
    assert r.status_code == 302
    db.session.expire_all()
    rows = LearnerAssignment.query.filter_by(learner_id=ann.id).order_by(LearnerAssignment.id).all()
    assert len(rows) == 2
    assert rows[0].tutor_id == people["tutor"].id and rows[0].ended_at is not None
    assert rows[1].tutor_id == people["tutor2"].id and rows[1].ended_at is None and rows[1].reason == "Caseload"
    assert db.session.get(Learner, ann.id).tutor_id == people["tutor2"].id


def test_reason_required_for_reassign(client, people, cohort):
    ann = cohort.test_learners[0]
    login(client, "admin@x.org")
    client.post(f"/learners/{ann.id}/reassign", data={"tutor_id": people["tutor2"].id, "cohort_id": cohort.id,
                                                       "effective_date": "2026-10-10", "reason": ""})
    assert LearnerAssignment.query.filter_by(learner_id=ann.id).count() == 1


def test_archive_removes_from_future_registers_but_keeps_records(client, people, cohort, monkeypatch):
    ann = cohort.test_learners[0]
    past = TrainingSession(cohort=cohort, tutor=cohort.tutor, session_type=SessionType.MONTHLY, title="Oct",
                           start_at=datetime(2026, 10, 6, 10, 0))
    future = TrainingSession(cohort=cohort, tutor=cohort.tutor, session_type=SessionType.MONTHLY, title="Nov",
                             start_at=datetime(2026, 11, 3, 10, 0))
    db.session.add_all([past, future])
    db.session.flush()
    db.session.add(Attendance(session_id=past.id, learner_id=ann.id, status="present"))
    db.session.commit()

    freeze(monkeypatch, datetime(2026, 10, 20, 9, 0))
    login(client, "admin@x.org")
    client.post(f"/learners/{ann.id}/archive", data={"leave_date": "2026-10-20", "leave_reason": "withdrawn"})
    db.session.expire_all()
    assert db.session.get(Learner, ann.id).is_archived
    assert ann.id in [l.id for l in db.session.get(TrainingSession, past.id).expected_learners()]
    assert ann.id not in [l.id for l in db.session.get(TrainingSession, future.id).expected_learners()]
    archived_page = client.get("/learners/?show=archived").data
    assert b"Able, Ann" in archived_page and b"Baker" not in archived_page
    assert b"Able, Ann" not in client.get("/learners/").data


def test_monthly_report_percentages(app, people, cohort, monkeypatch):
    freeze(monkeypatch, datetime(2026, 10, 31, 12, 0))
    ann, ben, cat = cohort.test_learners
    s1 = TrainingSession(cohort=cohort, tutor=cohort.tutor, session_type=SessionType.MONTHLY, title="Oct",
                         start_at=datetime(2026, 10, 6, 10, 0), register_completed_at=datetime(2026, 10, 6, 10, 5))
    s2 = TrainingSession(cohort=cohort, tutor=cohort.tutor, session_type=SessionType.ADDITIONAL, title="Extra",
                         start_at=datetime(2026, 10, 20, 10, 0))
    db.session.add_all([s1, s2])
    db.session.flush()
    for s, marks in [(s1, ["present", "late", "absent"]), (s2, ["present", "authorised", "absent"])]:
        for l, st in zip(cohort.test_learners, marks):
            db.session.add(Attendance(session_id=s.id, learner_id=l.id, status=st))
    db.session.commit()

    r = month_summary(2026, 10)
    assert r["overall"].expected == 6 and r["overall"].attended == 3
    assert round(r["overall"].pct, 1) == 50.0
    rows = {row["learner"].id: row for row in r["learner_rows"]}
    assert rows[ann.id]["tally"].pct == 100.0 and not rows[ann.id]["below"]
    assert rows[cat.id]["tally"].pct == 0.0 and rows[cat.id]["below"]
    assert rows[ben.id]["tally"].pct_excl_authorised == 100.0
    assert r["registers_on_time"] == 1 and len(r["registers_incomplete"]) == 1


def test_report_pages_and_csv(client, people, cohort):
    login(client, "admin@x.org")
    assert client.get("/reports/monthly?month=2026-10").status_code == 200
    r = client.get("/reports/monthly.csv?month=2026-10&kind=learners")
    assert r.status_code == 200 and r.mimetype == "text/csv"


def test_csv_neutralises_formulas():
    import io
    from app.reports import SafeCSVWriter
    buf = io.StringIO()
    SafeCSVWriter(buf).writerow(["=HYPERLINK(\"x\")", "ok"])
    assert "'=HYPERLINK" in buf.getvalue()
