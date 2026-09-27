"""Attendance reporting used by the monthly report, dashboards and CSV exports.

Attendance % = (Present + Late) / sessions the learner was expected at.
"Excl. authorised" also removes authorised absences from the denominator.
"""
import csv
from collections import Counter, defaultdict
from datetime import timedelta

from flask import current_app

from .extensions import db
from .models import (
    AlertStatus,
    Attendance,
    AttendanceStatus,
    Cohort,
    PastoralAlert,
    TrainingSession,
)
from .timeutil import add_months, month_bounds, month_label, now


class Tally:
    __slots__ = ("present", "late", "absent", "authorised")

    def __init__(self):
        self.present = self.late = self.absent = self.authorised = 0

    def add(self, status):
        setattr(self, status, getattr(self, status) + 1)

    @property
    def expected(self):
        return self.present + self.late + self.absent + self.authorised

    @property
    def attended(self):
        return self.present + self.late

    @property
    def pct(self):
        return 100.0 * self.attended / self.expected if self.expected else None

    @property
    def pct_excl_authorised(self):
        denom = self.expected - self.authorised
        return 100.0 * self.attended / denom if denom else None


def _session_query(start, end, course_id=None, cohort_id=None, tutor_id=None):
    q = TrainingSession.query.join(Cohort).filter(
        TrainingSession.start_at >= start, TrainingSession.start_at < end
    )
    if course_id:
        q = q.filter(Cohort.course_id == course_id)
    if cohort_id:
        q = q.filter(TrainingSession.cohort_id == cohort_id)
    if tutor_id:
        q = q.filter(TrainingSession.tutor_id == tutor_id)
    return q


def month_summary(year, month, course_id=None, cohort_id=None, tutor_id=None):
    start, end = month_bounds(year, month)
    threshold = current_app.config["ATTENDANCE_THRESHOLD"]
    grace = timedelta(minutes=current_app.config["PASTORAL_GRACE_MINUTES"])
    current = now()

    all_sessions = _session_query(start, end, course_id, cohort_id, tutor_id).order_by(TrainingSession.start_at).all()
    cancelled = [s for s in all_sessions if s.is_cancelled]
    delivered = [s for s in all_sessions if not s.is_cancelled and s.start_at <= current]
    session_ids = [s.id for s in delivered]

    marks = []
    if session_ids:
        marks = Attendance.query.filter(Attendance.session_id.in_(session_ids)).all()

    overall = Tally()
    by_learner = defaultdict(Tally)
    by_cohort = defaultdict(Tally)
    by_course = defaultdict(Tally)
    by_tutor = defaultdict(Tally)
    by_session = defaultdict(Tally)
    learners, cohorts, courses, tutors = {}, {}, {}, {}
    for m in marks:
        s = m.session
        overall.add(m.status)
        by_learner[m.learner_id].add(m.status)
        by_cohort[s.cohort_id].add(m.status)
        by_course[s.cohort.course_id].add(m.status)
        by_tutor[s.tutor_id].add(m.status)
        by_session[s.id].add(m.status)
        learners[m.learner_id] = m.learner
        cohorts[s.cohort_id] = s.cohort
        courses[s.cohort.course_id] = s.cohort.course
        tutors[s.tutor_id] = s.tutor

    learner_rows = sorted(
        (
            {"learner": learners[lid], "tally": t, "below": t.pct is not None and t.pct < threshold}
            for lid, t in by_learner.items()
        ),
        key=lambda r: (r["tally"].pct if r["tally"].pct is not None else 101, r["learner"].last_name),
    )

    def rows(tallies, lookup, label):
        out = [{"obj": lookup[k], "label": label(lookup[k]), "tally": t} for k, t in tallies.items()]
        return sorted(out, key=lambda r: r["label"])

    register_rows = []
    for s in delivered:
        on_time = s.register_completed_at is not None and s.register_completed_at <= s.start_at + grace
        register_rows.append({"session": s, "tally": by_session.get(s.id, Tally()), "on_time": on_time})

    alerts = []
    if session_ids:
        alerts = PastoralAlert.query.filter(PastoralAlert.session_id.in_(session_ids)).all()
    outcome_counts = Counter(a.outcome_label or "Awaiting outcome" for a in alerts)

    return {
        "year": year,
        "month": month,
        "label": month_label(year, month),
        "threshold": threshold,
        "overall": overall,
        "learner_rows": learner_rows,
        "below_threshold": [r for r in learner_rows if r["below"]],
        "by_course": rows(by_course, courses, lambda c: c.title),
        "by_cohort": rows(by_cohort, cohorts, lambda c: c.name),
        "by_tutor": rows(by_tutor, tutors, lambda u: u.name if u else "Unassigned"),
        "registers": register_rows,
        "registers_incomplete": [r for r in register_rows if r["session"].register_completed_at is None],
        "registers_on_time": sum(1 for r in register_rows if r["on_time"]),
        "sessions_delivered": len(delivered),
        "sessions_cancelled": cancelled,
        "alerts_total": len(alerts),
        "alerts_open": sum(1 for a in alerts if a.status != AlertStatus.CLOSED),
        "alert_outcomes": sorted(outcome_counts.items(), key=lambda kv: -kv[1]),
    }


def trend(year, month, months=6, course_id=None, cohort_id=None, tutor_id=None):
    """Attendance % for each of the last `months` months, oldest first."""
    points = []
    for offset in range(months - 1, -1, -1):
        y, m = add_months(year, month, -offset)
        start, end = month_bounds(y, m)
        ids = [
            s.id
            for s in _session_query(start, end, course_id, cohort_id, tutor_id)
            .filter(TrainingSession.cancelled_at.is_(None))
            .all()
        ]
        t = Tally()
        if ids:
            for (status,) in db.session.query(Attendance.status).filter(Attendance.session_id.in_(ids)):
                t.add(status)
        points.append({"label": month_label(y, m)[:3] + f" {y}", "tally": t})
    return points


STATUS_ORDER = [
    AttendanceStatus.PRESENT,
    AttendanceStatus.LATE,
    AttendanceStatus.ABSENT,
    AttendanceStatus.AUTHORISED,
]


class SafeCSVWriter:
    """csv.writer that neutralises spreadsheet formulas (CSV injection)."""

    def __init__(self, buf):
        self._w = csv.writer(buf)

    @staticmethod
    def _clean(value):
        if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
            return "'" + value
        return value

    def writerow(self, row):
        self._w.writerow([self._clean(v) for v in row])
