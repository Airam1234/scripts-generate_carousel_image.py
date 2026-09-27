import json
import secrets
from datetime import timedelta

from flask_login import UserMixin
from sqlalchemy import event, or_
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .timeutil import now


class Role:
    ADMIN = "admin"
    TUTOR = "tutor"
    PASTORAL = "pastoral"
    INSPECTOR = "inspector"

    LABELS = {
        ADMIN: "Administrator",
        TUTOR: "Tutor",
        PASTORAL: "Pastoral Support",
        INSPECTOR: "Inspector (read-only)",
    }
    ALL = list(LABELS)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Rotated on password change / deactivation so existing sessions are invalidated.
    login_id = db.Column(db.String(64), unique=True, nullable=False, default=lambda: secrets.token_hex(32))
    active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=True)
    failed_logins = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # e.g. time-limited inspector accounts
    created_at = db.Column(db.DateTime, nullable=False, default=now)

    def get_id(self):
        return self.login_id

    @property
    def is_active(self):
        return self.active and (self.expires_at is None or self.expires_at > now())

    @property
    def is_locked(self):
        return self.locked_until is not None and self.locked_until > now()

    @property
    def role_label(self):
        return Role.LABELS.get(self.role, self.role)

    def has_role(self, *roles):
        return self.role in roles

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.login_id = secrets.token_hex(32)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    standard_ref = db.Column(db.String(20))  # IfATE standard reference, e.g. ST0070
    active = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def title(self):
        return f"{self.name} Level {self.level}"


DEFAULT_COURSES = [
    ("Business Administrator", 3),
    ("Admin Assistant", 2),
    ("Operations / Departmental Manager", 5),
    ("Team Leader / Supervisor", 3),
    ("Pharmacy Assistant", 2),
    ("Pharmacy Technician", 3),
]


class Cohort(db.Model):
    __tablename__ = "cohorts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    start_date = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=now)

    course = db.relationship("Course")
    tutor = db.relationship("User")

    @property
    def current_learners(self):
        return (
            Learner.query.filter_by(cohort_id=self.id, archived_at=None)
            .order_by(Learner.last_name, Learner.first_name)
            .all()
        )


class LearnerStatus:
    ACTIVE = "active"
    BREAK = "break_in_learning"
    LABELS = {ACTIVE: "Active", BREAK: "Break in learning"}


class LeaveReason:
    LABELS = {
        "completed": "Completed / achieved",
        "withdrawn": "Withdrawn",
        "transferred": "Transferred to another provider",
        "employment_ended": "Employment ended",
        "other": "Other",
    }


class Learner(db.Model):
    __tablename__ = "learners"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    uln = db.Column(db.String(10), unique=True)  # Unique Learner Number
    email = db.Column(db.String(255))
    phone = db.Column(db.String(40))
    employer_name = db.Column(db.String(160))
    employer_contact = db.Column(db.String(255))
    cohort_id = db.Column(db.Integer, db.ForeignKey("cohorts.id"), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    start_date = db.Column(db.Date, nullable=False)
    planned_end_date = db.Column(db.Date)
    status = db.Column(db.String(30), nullable=False, default=LearnerStatus.ACTIVE)
    archived_at = db.Column(db.DateTime)
    archived_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    leave_date = db.Column(db.Date)
    leave_reason = db.Column(db.String(30))
    leave_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=now)

    cohort = db.relationship("Cohort")
    tutor = db.relationship("User", foreign_keys=[tutor_id])
    archived_by = db.relationship("User", foreign_keys=[archived_by_id])
    assignments = db.relationship(
        "LearnerAssignment", order_by="LearnerAssignment.assigned_at", back_populates="learner"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_archived(self):
        return self.archived_at is not None

    @property
    def status_label(self):
        if self.is_archived:
            return "Archived – " + LeaveReason.LABELS.get(self.leave_reason, "left")
        return LearnerStatus.LABELS.get(self.status, self.status)

    @property
    def current_assignment(self):
        for a in reversed(self.assignments):
            if a.ended_at is None:
                return a
        return None


class LearnerAssignment(db.Model):
    """Append-only history of which tutor and cohort a learner was with, and when.

    Reassignment closes the current row (ended_at) and opens a new one, so the
    full trail is preserved for inspection.
    """

    __tablename__ = "learner_assignments"

    id = db.Column(db.Integer, primary_key=True)
    learner_id = db.Column(db.Integer, db.ForeignKey("learners.id"), nullable=False, index=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    cohort_id = db.Column(db.Integer, db.ForeignKey("cohorts.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime)
    reason = db.Column(db.Text)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recorded_at = db.Column(db.DateTime, nullable=False, default=now)

    learner = db.relationship("Learner", back_populates="assignments")
    tutor = db.relationship("User", foreign_keys=[tutor_id])
    cohort = db.relationship("Cohort")
    assigned_by = db.relationship("User", foreign_keys=[assigned_by_id])


class SessionType:
    FIRST_DAY = "first_day"
    MONTHLY = "monthly"
    ADDITIONAL = "additional"
    LABELS = {
        FIRST_DAY: "First day of learning (new starts)",
        MONTHLY: "Monthly session",
        ADDITIONAL: "Additional session",
    }


class DeliveryMode:
    LABELS = {"online": "Online", "in_person": "In person", "blended": "Blended"}


class TrainingSession(db.Model):
    __tablename__ = "training_sessions"

    id = db.Column(db.Integer, primary_key=True)
    cohort_id = db.Column(db.Integer, db.ForeignKey("cohorts.id"), nullable=False, index=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    session_type = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, nullable=False, default=180)
    delivery_mode = db.Column(db.String(20), nullable=False, default="online")
    location = db.Column(db.String(255))
    schedule_override_reason = db.Column(db.Text)
    cancelled_at = db.Column(db.DateTime)
    cancel_reason = db.Column(db.Text)
    register_completed_at = db.Column(db.DateTime)
    # Set once the 15-minute pastoral check has run for this session.
    pastoral_processed_at = db.Column(db.DateTime)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, nullable=False, default=now)

    cohort = db.relationship("Cohort")
    tutor = db.relationship("User", foreign_keys=[tutor_id])
    attendance = db.relationship("Attendance", back_populates="session")

    @property
    def end_at(self):
        return self.start_at + timedelta(minutes=self.duration_minutes)

    @property
    def type_label(self):
        return SessionType.LABELS.get(self.session_type, self.session_type)

    @property
    def is_cancelled(self):
        return self.cancelled_at is not None

    def expected_learners(self):
        """Learners who were placed in this cohort when the session started."""
        placed = (
            db.session.query(LearnerAssignment.learner_id)
            .filter(
                LearnerAssignment.cohort_id == self.cohort_id,
                LearnerAssignment.assigned_at <= self.start_at,
                or_(LearnerAssignment.ended_at.is_(None), LearnerAssignment.ended_at > self.start_at),
            )
        )
        marked = db.session.query(Attendance.learner_id).filter(Attendance.session_id == self.id)
        session_day = self.start_at.date()
        return (
            Learner.query.filter(
                or_(
                    Learner.id.in_(marked),
                    db.and_(
                        Learner.id.in_(placed),
                        or_(Learner.leave_date.is_(None), Learner.leave_date >= session_day),
                    ),
                )
            )
            .order_by(Learner.last_name, Learner.first_name)
            .all()
        )


class AttendanceStatus:
    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    AUTHORISED = "authorised"
    LABELS = {
        PRESENT: "Present",
        LATE: "Late",
        ABSENT: "Absent",
        AUTHORISED: "Authorised absence",
    }
    ATTENDED = {PRESENT, LATE}


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (db.UniqueConstraint("session_id", "learner_id", name="uq_attendance_session_learner"),)

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("training_sessions.id"), nullable=False, index=True)
    learner_id = db.Column(db.Integer, db.ForeignKey("learners.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)
    minutes_late = db.Column(db.Integer)
    note = db.Column(db.String(500))
    # True when the system recorded the absence because no mark was made within 15 minutes.
    auto_recorded = db.Column(db.Boolean, nullable=False, default=False)
    marked_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    marked_at = db.Column(db.DateTime, nullable=False, default=now)

    session = db.relationship("TrainingSession", back_populates="attendance")
    learner = db.relationship("Learner")
    marked_by = db.relationship("User")

    @property
    def status_label(self):
        return AttendanceStatus.LABELS.get(self.status, self.status)


class AlertStatus:
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    LABELS = {OPEN: "Open", IN_PROGRESS: "Contact attempted", CLOSED: "Closed"}


class AlertOutcome:
    LABELS = {
        "joined_late": "Learner contacted – joined session late",
        "reason_given": "Learner contacted – reason for absence given",
        "no_contact": "Unable to contact learner",
        "employer_contacted": "Employer contacted",
        "safeguarding": "Safeguarding / wellbeing concern – referred to DSL",
        "attended": "Tutor updated register – learner attended",
        "other": "Other",
    }


class ContactMethod:
    LABELS = {"phone": "Phone", "email": "Email", "text": "Text message", "teams": "Teams", "other": "Other"}


class PastoralAlert(db.Model):
    __tablename__ = "pastoral_alerts"
    __table_args__ = (db.UniqueConstraint("session_id", "learner_id", name="uq_alert_session_learner"),)

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("training_sessions.id"), nullable=False, index=True)
    learner_id = db.Column(db.Integer, db.ForeignKey("learners.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=AlertStatus.OPEN)
    outcome = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, nullable=False, default=now)
    closed_at = db.Column(db.DateTime)
    closed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    session = db.relationship("TrainingSession")
    learner = db.relationship("Learner")
    closed_by = db.relationship("User")
    contacts = db.relationship("PastoralContact", order_by="PastoralContact.contacted_at", back_populates="alert")

    @property
    def status_label(self):
        return AlertStatus.LABELS.get(self.status, self.status)

    @property
    def outcome_label(self):
        return AlertOutcome.LABELS.get(self.outcome, "") if self.outcome else ""


class PastoralContact(db.Model):
    """Each attempt Pastoral Support makes to reach a learner."""

    __tablename__ = "pastoral_contacts"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("pastoral_alerts.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    contacted_at = db.Column(db.DateTime, nullable=False, default=now)
    method = db.Column(db.String(20))
    outcome = db.Column(db.String(30))
    notes = db.Column(db.Text)

    alert = db.relationship("PastoralAlert", back_populates="contacts")
    user = db.relationship("User")

    @property
    def method_label(self):
        return ContactMethod.LABELS.get(self.method, self.method or "System")

    @property
    def outcome_label(self):
        return AlertOutcome.LABELS.get(self.outcome, "") if self.outcome else ""


class EmailLog(db.Model):
    __tablename__ = "email_log"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=now)
    recipients = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent = db.Column(db.Boolean, nullable=False, default=False)
    error = db.Column(db.Text)


class AuditLog(db.Model):
    """Append-only record of every change. Rows can never be updated or deleted."""

    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    at = db.Column(db.DateTime, nullable=False, default=now, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_label = db.Column(db.String(255))
    action = db.Column(db.String(60), nullable=False, index=True)
    entity_type = db.Column(db.String(40), index=True)
    entity_id = db.Column(db.Integer, index=True)
    summary = db.Column(db.String(500))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(64))

    user = db.relationship("User")

    @property
    def details_dict(self):
        try:
            return json.loads(self.details) if self.details else {}
        except ValueError:
            return {}


class AuditImmutableError(RuntimeError):
    pass


@event.listens_for(AuditLog, "before_update")
def _block_audit_update(mapper, connection, target):
    raise AuditImmutableError("Audit log entries cannot be modified")


@event.listens_for(AuditLog, "before_delete")
def _block_audit_delete(mapper, connection, target):
    raise AuditImmutableError("Audit log entries cannot be deleted")


def seed_courses():
    if Course.query.count() == 0:
        for name, level in DEFAULT_COURSES:
            db.session.add(Course(name=name, level=level))
        db.session.commit()
