import io

from flask import Blueprint, Response, render_template, request
from flask_login import current_user, login_required

from ..audit import audit
from ..extensions import db
from ..models import Cohort, Course, Role, User
from ..reports import SafeCSVWriter, month_summary, trend
from ..timeutil import parse_month

bp = Blueprint("reports", __name__, url_prefix="/reports")


def _filters():
    year, month = parse_month(request.args.get("month"))
    f = {
        "course_id": request.args.get("course_id", type=int),
        "cohort_id": request.args.get("cohort_id", type=int),
        "tutor_id": request.args.get("tutor_id", type=int),
    }
    if current_user.role == Role.TUTOR:
        f["tutor_id"] = current_user.id  # tutors only ever see their own delivery
    return year, month, f


@bp.route("/monthly")
@login_required
def monthly():
    year, month, f = _filters()
    summary = month_summary(year, month, **f)
    cohorts = Cohort.query.order_by(Cohort.name)
    if current_user.role == Role.TUTOR:
        cohorts = cohorts.filter_by(tutor_id=current_user.id)
    return render_template(
        "reports/monthly.html", r=summary, trend=trend(year, month, **f), filters=f,
        month_value=f"{year:04d}-{month:02d}", courses=Course.query.order_by(Course.name).all(),
        cohorts=cohorts.all(), tutors=User.query.filter_by(role=Role.TUTOR).order_by(User.name).all(),
    )


@bp.route("/monthly.csv")
@login_required
def monthly_csv():
    year, month, f = _filters()
    r = month_summary(year, month, **f)
    kind = "sessions" if request.args.get("kind") == "sessions" else "learners"
    buf = io.StringIO()
    w = SafeCSVWriter(buf)
    if kind == "sessions":
        w.writerow(["Date", "Start", "Session", "Type", "Cohort", "Course", "Tutor", "Expected", "Present",
                    "Late", "Absent", "Authorised", "Attendance %", "Register completed", "Completed within 15 min"])
        for row in r["registers"]:
            s, t = row["session"], row["tally"]
            w.writerow([s.start_at.date().isoformat(), s.start_at.strftime("%H:%M"), s.title, s.type_label,
                        s.cohort.name, s.cohort.course.title, s.tutor.name if s.tutor else "", t.expected,
                        t.present, t.late, t.absent, t.authorised, _pct(t.pct),
                        s.register_completed_at.isoformat(" ") if s.register_completed_at else "Not completed",
                        "Yes" if row["on_time"] else "No"])
        for s in r["sessions_cancelled"]:
            w.writerow([s.start_at.date().isoformat(), s.start_at.strftime("%H:%M"), s.title, s.type_label,
                        s.cohort.name, s.cohort.course.title, s.tutor.name if s.tutor else "",
                        "", "", "", "", "", "", f"CANCELLED: {s.cancel_reason}", ""])
    else:
        w.writerow(["Learner", "ULN", "Course", "Cohort", "Tutor", "Status", "Expected", "Present", "Late",
                    "Absent", "Authorised", "Attendance %", "Attendance % excl. authorised",
                    f"Below {r['threshold']:g}%"])
        for row in r["learner_rows"]:
            l, t = row["learner"], row["tally"]
            w.writerow([l.full_name, l.uln or "", l.cohort.course.title, l.cohort.name,
                        l.tutor.name if l.tutor else "", l.status_label, t.expected, t.present, t.late, t.absent,
                        t.authorised, _pct(t.pct), _pct(t.pct_excl_authorised), "Yes" if row["below"] else "No"])
    audit("report.exported", summary=f"Exported {kind} attendance CSV for {r['label']}", details=f)
    db.session.commit()
    filename = f"attendance-{kind}-{year:04d}-{month:02d}.csv"
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


def _pct(value):
    return "" if value is None else f"{value:.1f}"

