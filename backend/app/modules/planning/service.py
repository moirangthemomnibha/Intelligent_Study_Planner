"""
Planning Service

Responsibilities:
1. Calculate topic priorities.
2. Generate study schedules.
3. Retrieve planning settings.
4. Save planning settings.
5. Persist generated study sessions.
6. Prevent duplicate planned sessions.
7. Retrieve student study sessions.
"""

from datetime import date, timedelta

from sqlmodel import Session, select

from app.planning.priority import calculate_priority
from app.planning.scheduler import build_schedule

from app.modules.planning.models import PlanSettings
from app.modules.sessions.models import StudySession
from app.modules.topics.models import Topic
from app.modules.subjects.models import Subject


# ==================================================
# 1. GENERATE TOPIC EXPLANATION
# ==================================================

def generate_topic_reason(topic: dict) -> str:
    """Explain why a topic received its priority."""

    reasons = []

    if topic.get("days_to_exam", 30) <= 7:
        reasons.append("exam is approaching")

    if topic.get("difficulty", 3) >= 4:
        reasons.append("high difficulty")

    if topic.get("confidence", 3) <= 2:
        reasons.append("low confidence")

    if topic.get("completion_percent", 0) < 50:
        reasons.append("topic is unfinished")

    if not reasons:
        return "Scheduled according to calculated topic priority."

    return "Prioritized because of " + ", ".join(reasons) + "."


# ==================================================
# 2. GENERATE STUDY PLAN
# ==================================================

def generate_plan(
    topics: list[dict],
    available_minutes: int,
    days: int,
    start_date: date | None = None,
    preferred_times: list | None = None
) -> list[dict]:

    ranked_topics = []

    for topic in topics:
        priority_score = calculate_priority(topic)

        ranked_topics.append({
            **topic,
            "priority_score": priority_score,
            "reason": generate_topic_reason(topic)
        })

    ranked_topics.sort(
        key=lambda topic: topic["priority_score"],
        reverse=True
    )

    return build_schedule(
        topics=ranked_topics,
        available_minutes=available_minutes,
        days=days,
        start_date=start_date,
        preferred_times=preferred_times
    )


# ==================================================
# 3. GET PLAN SETTINGS
# ==================================================

def get_plan_settings(
    session: Session,
    student_id: int
):
    """Retrieve existing planning settings."""

    return session.exec(
        select(PlanSettings).where(
            PlanSettings.student_id == student_id
        )
    ).first()


# ==================================================
# 4. SAVE PLAN SETTINGS
# ==================================================

def save_plan_settings(
    session: Session,
    student_id: int,
    start: date,
    days: int
):
    """Create or update planning settings."""

    settings = get_plan_settings(
        session,
        student_id
    )

    if settings:

        settings.plan_start = start
        settings.plan_days = days

    else:

        settings = PlanSettings(
            student_id=student_id,
            plan_start=start,
            plan_days=days
        )

        session.add(settings)

    session.commit()
    session.refresh(settings)

    return settings


# ==================================================
# 5. PERSIST GENERATED STUDY SESSIONS
# ==================================================

def persist_generated_sessions(
    session: Session,
    student_id: int,
    generated_plan: list[dict],
    start_date: date,
    days: int
) -> list[StudySession]:
    """
    Save generated sessions into SQLite.

    Existing planned sessions within the new planning
    period are replaced.

    Completed, missed and partial sessions are preserved.

    Every topic must belong to the specified student.
    """

    saved_sessions = []

    if days < 1:
        raise ValueError("Planning period must be at least one day.")

    end_date = start_date + timedelta(days=days - 1)

    try:

        # ------------------------------------------
        # VERIFY TOPIC OWNERSHIP
        # ------------------------------------------

        owned_topics = session.exec(
            select(Topic)
            .join(
                Subject,
                Topic.subject_id == Subject.id
            )
            .where(
                Subject.student_id == student_id
            )
        ).all()

        owned_topic_ids = {
            topic.id for topic in owned_topics
        }

        for item in generated_plan:

            topic_id = item.get("topic_id")

            if topic_id not in owned_topic_ids:
                raise ValueError(
                    "Cannot save a study session for a topic "
                    "that does not belong to this student."
                )

        # ------------------------------------------
        # FIND EXISTING PLANNED SESSIONS
        # ------------------------------------------

        statement = select(StudySession).where(
            StudySession.student_id == student_id,
            StudySession.status == "planned",
            StudySession.planned_date >= start_date.isoformat(),
            StudySession.planned_date <= end_date.isoformat()
        )

        existing_sessions = session.exec(statement).all()

        # ------------------------------------------
        # REMOVE ONLY OLD PLANNED SESSIONS
        # ------------------------------------------

        for old_session in existing_sessions:
            session.delete(old_session)

        # ------------------------------------------
        # INSERT NEW GENERATED SESSIONS
        # ------------------------------------------

        for item in generated_plan:

            study_session = StudySession(
                student_id=student_id,
                topic_id=item["topic_id"],
                planned_date=item["day"],
                planned_minutes=item["duration_minutes"],
                actual_minutes=None,
                status="planned",
                reflection=None
            )

            session.add(study_session)
            saved_sessions.append(study_session)

        # ------------------------------------------
        # COMMIT CHANGES
        # ------------------------------------------

        session.commit()

        for study_session in saved_sessions:
            session.refresh(study_session)

        return saved_sessions

    except Exception:

        session.rollback()
        raise


# ==================================================
# 6. GET STUDENT STUDY SESSIONS
# ==================================================

def get_student_sessions(
    session: Session,
    student_id: int
) -> list[StudySession]:
    """Retrieve all study sessions belonging to a student."""

    statement = select(StudySession).where(
        StudySession.student_id == student_id
    ).order_by(
        StudySession.planned_date
    )

    return session.exec(statement).all()