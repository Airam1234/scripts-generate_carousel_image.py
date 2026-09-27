import random
from datetime import date, datetime, time, timedelta

import click

from .audit import audit
from .extensions import db
from .models import (
    Attendance,
    AttendanceStatus,
    Cohort,
    Course,
    Learner,
    Role,
    SessionType,
    TrainingSession,
    User,
)
from .notifications import process_due_sessions
from .security import password_problems
from .services import place_learner
from .timeutil import add_months, now, weekday_in_first_week


def register_cli(app):
    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt=True)
    @click.password_option()
    def create_admin(email, name, password):
        """Create the first administrator account."""
        email = email.strip().lower()
        problems = password_problems(password, email)
        if problems:
            raise click.ClickException(" ".join(problems))
        if User.query.filter_by(email=email).first():
            raise click.ClickException("A user with that email already exists.")
        user = User(email=email, name=name.strip(), role=Role.ADMIN, must_change_password=False)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        audit("user.created", user, f"Created administrator {email} from the command line")
        db.session.commit()
        click.echo(f"Administrator {email} created.")

    @app.cli.command("process-alerts")
    def process_alerts():
        """Run the 15-minute pastoral check now (for use from cron)."""
        count = process_due_sessions()
        click.echo(f"Processed {count} session(s).")

    @app.cli.command("seed-demo")
    @click.option("--password", default="DemoPassword123!", show_default=True)
    def seed_demo(password):
        """Load demo tutors, cohorts, learners and sessions. NOT for production."""
        if app.config["APP_ENV"] == "production":
            raise click.ClickException("Refusing to load demo data in production.")
        if User.query.count():
            raise click.ClickException("Database already has users – demo data is only for an empty database.")
        random.seed(42)

        def mk(email, name, role):
            u = User(email=email, name=name, role=role, must_change_password=False)
            u.set_password(password)
            db.session.add(u)
            return u

        admin = mk("admin@example.org", "Alex Admin", Role.ADMIN)
        mk("pastoral@example.org", "Pat Pastoral", Role.PASTORAL)
        mk("inspector@example.org", "Ivy Inspector", Role.INSPECTOR)
        tutors = [mk(f"tutor{i}@example.org", n, Role.TUTOR)
                  for i, n in enumerate(["Sam Patel", "Jordan Hughes", "Morgan Clarke"], 1)]
        db.session.flush()

        first = ["Amelia", "Oliver", "Isla", "Noah", "Ava", "Leo", "Mia", "Jack", "Grace", "Harry",
                 "Freya", "Oscar", "Ella", "George", "Lily", "Arthur", "Evie", "Theo"]
        last = ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies",
                "Robinson", "Wright", "Thompson", "Evans", "Walker", "White", "Roberts", "Green"]
        today_ = now().date()
        y, m = add_months(today_.year, today_.month, -3)
        cohort_start = date(y, m, 18)

        uln = 1000000000
        for idx, course in enumerate(Course.query.order_by(Course.id)):
            tutor = tutors[idx % len(tutors)]
            cohort = Cohort(name=f"{course.name.split(' /')[0]} L{course.level} – {cohort_start:%b %Y}",
                            course=course, tutor=tutor, start_date=cohort_start)
            db.session.add(cohort)
            db.session.flush()
            learners = []
            for _ in range(6):
                uln += 1
                learner = Learner(first_name=random.choice(first), last_name=random.choice(last), uln=str(uln),
                                  email=f"learner{uln}@example.org", phone="07700 900000",
                                  employer_name="Example Employer Ltd", cohort=cohort, tutor=tutor,
                                  start_date=cohort_start)
                db.session.add(learner)
                db.session.flush()
                place_learner(learner, tutor, cohort, datetime.combine(cohort_start, time()), "Enrolled", admin)
                learners.append(learner)

            sessions = [TrainingSession(cohort=cohort, tutor=tutor, session_type=SessionType.FIRST_DAY,
                                        title=f"{cohort.name} – First day of learning",
                                        start_at=datetime.combine(cohort_start, time(9, 30)))]
            for i in range(1, 5):
                sy, sm = add_months(cohort_start.year, cohort_start.month, i)
                day = weekday_in_first_week(sy, sm, 1 + idx % 3)
                sessions.append(TrainingSession(cohort=cohort, tutor=tutor, session_type=SessionType.MONTHLY,
                                                title=f"{cohort.name} – Monthly session ({day:%B %Y})",
                                                start_at=datetime.combine(day, time(10, 0))))
            for s in sessions:
                s.created_by_id = admin.id
                db.session.add(s)
                db.session.flush()
                if s.start_at < now():
                    s.pastoral_processed_at = s.start_at + timedelta(minutes=15)
                    s.register_completed_at = s.start_at + timedelta(minutes=random.choice([5, 10, 40]))
                    for learner in learners:
                        status = random.choices(
                            [AttendanceStatus.PRESENT, AttendanceStatus.LATE, AttendanceStatus.ABSENT,
                             AttendanceStatus.AUTHORISED], weights=[78, 8, 10, 4])[0]
                        db.session.add(Attendance(session_id=s.id, learner_id=learner.id, status=status,
                                                  minutes_late=10 if status == AttendanceStatus.LATE else None,
                                                  marked_by_id=tutor.id, marked_at=s.register_completed_at))
        audit("system.demo_seeded", summary="Demo data loaded", user=admin)
        db.session.commit()
        click.echo(f"Demo data loaded. Sign in as admin@example.org / tutor1@example.org / "
                   f"pastoral@example.org / inspector@example.org with password {password}")
