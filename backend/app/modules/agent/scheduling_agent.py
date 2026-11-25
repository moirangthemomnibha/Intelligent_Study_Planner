from datetime import date, timedelta
from sqlmodel import Session, select

from app.modules.sessions.models import StudySession
from app.modules.topics.models import Topic


def detect_missed_sessions(
    session: Session,
    student_id: int,
) -> list:

    today = date.today()

    sessions = session.exec(
        select(StudySession)
        .where(StudySession.student_id == student_id)
        .where(StudySession.status == "planned")
    ).all()

    missed = []

    for item in sessions:

        try:
            planned_day = date.fromisoformat(
                item.planned_date
            )
        except (ValueError, TypeError):
            continue

        if planned_day < today:
            item.status = "missed"

            missed.append({
                "session_id": item.id,
                "topic_id": item.topic_id,
                "planned_date": item.planned_date,
                "planned_minutes": item.planned_minutes,
            })

    session.commit()

    return missed


def reschedule_missed_sessions(
    session: Session,
    student_id: int,
    available_minutes_per_day: int = 180,
) -> dict:

    if available_minutes_per_day <= 0:
        raise ValueError("Available time must be positive.")

    missed_sessions = session.exec(
        select(StudySession)
        .where(StudySession.student_id == student_id)
        .where(StudySession.status == "missed")
    ).all()

    if not missed_sessions:
        return {
            "message": "No missed sessions found.",
            "rescheduled": 0,
        }

    today = date.today()
    daily_totals = {}

    rescheduled = 0

    for item in missed_sessions:

        duration = item.planned_minutes

        if duration <= 0 or duration > 90:
            continue

        topic = session.get(Topic, item.topic_id)

        if topic is None:
            continue

        target_day = today

        while True:

            day_key = target_day.isoformat()

            existing_total = daily_totals.get(day_key, 0)

            if existing_total + duration <= available_minutes_per_day:
                break

            target_day += timedelta(days=1)

        daily_totals[day_key] = existing_total + duration

        if item.original_planned_date is None:
            item.original_planned_date = item.planned_date

        item.planned_date = day_key
        item.status = "planned"
        item.rescheduled_count += 1
        item.missed_reason = "Automatically rescheduled."

        rescheduled += 1

    session.commit()

    return {
        "message": "Missed sessions rescheduled.",
        "rescheduled": rescheduled,
    }