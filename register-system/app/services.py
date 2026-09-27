"""Operations that change several records at once and must leave an audit trail."""
from .audit import audit
from .extensions import db
from .models import LearnerAssignment, TrainingSession
from .timeutil import now


def place_learner(learner, tutor, cohort, effective_at, reason, by):
    """Start a learner's first placement (used when a learner is created)."""
    db.session.add(LearnerAssignment(
        learner=learner, tutor_id=tutor.id if tutor else None, cohort_id=cohort.id,
        assigned_at=effective_at, reason=reason, assigned_by_id=by.id,
    ))


def reassign_learner(learner, tutor, cohort, effective_at, reason, by):
    """Move a learner to a new tutor and/or cohort. History rows are never edited
    other than closing the current placement."""
    old_tutor, old_cohort = learner.tutor, learner.cohort
    current = learner.current_assignment
    if current is not None:
        current.ended_at = effective_at
    db.session.add(LearnerAssignment(
        learner=learner, tutor_id=tutor.id if tutor else None, cohort_id=cohort.id,
        assigned_at=effective_at, reason=reason, assigned_by_id=by.id,
    ))
    learner.tutor_id = tutor.id if tutor else None
    learner.cohort_id = cohort.id
    audit(
        "learner.reassigned",
        learner,
        f"{learner.full_name}: {old_tutor.name if old_tutor else 'no tutor'} ({old_cohort.name}) → "
        f"{tutor.name if tutor else 'no tutor'} ({cohort.name})",
        {
            "from_tutor": old_tutor.email if old_tutor else None,
            "to_tutor": tutor.email if tutor else None,
            "from_cohort": old_cohort.name,
            "to_cohort": cohort.name,
            "effective_at": effective_at,
            "reason": reason,
        },
        user=by,
    )


def change_cohort_tutor(cohort, new_tutor, reason, by, move_learners=True, move_sessions=True):
    old_tutor = cohort.tutor
    cohort.tutor_id = new_tutor.id if new_tutor else None
    moved_learners = moved_sessions = 0
    at = now()
    if move_learners:
        for learner in cohort.current_learners:
            if learner.tutor_id == (old_tutor.id if old_tutor else None):
                reassign_learner(learner, new_tutor, cohort, at, f"Cohort tutor changed: {reason}", by)
                moved_learners += 1
    if move_sessions:
        for s in TrainingSession.query.filter(
            TrainingSession.cohort_id == cohort.id,
            TrainingSession.start_at > at,
            TrainingSession.cancelled_at.is_(None),
        ):
            s.tutor_id = new_tutor.id if new_tutor else None
            moved_sessions += 1
    audit(
        "cohort.tutor_changed",
        cohort,
        f"{cohort.name}: tutor {old_tutor.name if old_tutor else 'none'} → {new_tutor.name if new_tutor else 'none'}",
        {"reason": reason, "learners_moved": moved_learners, "future_sessions_moved": moved_sessions},
        user=by,
    )
    return moved_learners, moved_sessions
