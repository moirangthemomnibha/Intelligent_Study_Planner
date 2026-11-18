"""Controlled agent orchestration for the study planner."""

import re
from datetime import date

from sqlmodel import Session, select

from app.modules.students.models import Student
from app.modules.subjects.models import Subject
from app.modules.topics.models import Topic
from app.modules.sessions.models import StudySession

from app.modules.ai.service import recommend_next_action
from app.modules.planning.service import generate_plan


ALLOWED_TOOLS = {
    "get_student_summary",
    "get_deadline_risks",
    "simulate_schedule",
    "propose_reschedule",
}


def get_student_summary(session: Session, student_id: int) -> dict:
    """Observe the student's subjects, topics and study progress."""

    student = session.get(Student, student_id)

    if student is None:
        raise ValueError("Student not found.")

    statement = (
        select(Topic, Subject)
        .join(Subject, Topic.subject_id == Subject.id)
        .where(Subject.student_id == student_id)
    )

    results = session.exec(statement).all()

    topics = []

    for topic, subject in results:
        try:
            days_to_exam = (
                date.fromisoformat(subject.exam_date) - date.today()
            ).days
        except (ValueError, TypeError):
            days_to_exam = 30

        topics.append({
            "id": topic.id,
            "topic_id": topic.id,
            "name": topic.name,
            "estimated_minutes": topic.estimated_minutes,
            "difficulty": topic.difficulty,
            "completion_percent": topic.completion_percent,
            "confidence": topic.confidence,
            "priority": topic.priority,
            "exam_weight": subject.exam_weight,
            "days_to_exam": days_to_exam,
        })

    sessions = session.exec(
        select(StudySession).where(
            StudySession.student_id == student_id
        )
    ).all()

    return {
        "student_id": student_id,
        "topics": topics,
        "sessions": [
            {
                "id": item.id,
                "topic_id": item.topic_id,
                "date": item.planned_date,
                "status": item.status,
                "planned_minutes": item.planned_minutes,
                "actual_minutes": item.actual_minutes,
            }
            for item in sessions
        ],
    }


def get_deadline_risks(topics: list[dict]) -> list[str]:
    """Identify unfinished topics with approaching exams."""

    risks = []

    for topic in topics:
        if (
            topic["completion_percent"] < 100
            and topic["days_to_exam"] <= 7
        ):
            risks.append(
                f'{topic["name"]}: exam approaching with '
                f'{100 - topic["completion_percent"]}% remaining.'
            )

    return risks


def extract_available_minutes(
    intent: str,
    default_minutes: int
) -> int:
    """Extract an explicitly mentioned study duration."""

    match = re.search(
        r"(\d+)\s*(minutes?|mins?)",
        intent.lower()
    )

    if match:
        return max(1, int(match.group(1)))

    return default_minutes


def run_agent(
    session: Session,
    student_id: int,
    intent: str,
    available_minutes: int,
    horizon_days: int,
    approval_mode: str,
) -> dict:
    """
    Agent workflow:
    Observe -> Reason -> Propose -> Validate.
    """

    # 1. OBSERVE
    summary = get_student_summary(session, student_id)
    topics = summary["topics"]

    if not topics:
        return {
            "summary": "Add subjects and topics before generating a study plan.",
            "actions": [],
            "requires_confirmation": False,
        }

    # 2. REASON
    recommendation = recommend_next_action(summary)
    deadline_risks = get_deadline_risks(topics)

    # Understand available time from the student's instruction.
    available_minutes = extract_available_minutes(
        intent,
        available_minutes
    )

    if "today" in intent.lower():
        horizon_days = 1

    # 3. PROPOSE
    start_date = date.today()

    generated_plan = generate_plan(
        topics=topics,
        available_minutes=available_minutes,
        days=horizon_days,
        start_date=start_date,
    )

    # 4. VALIDATE
    daily_totals = {}

    for item in generated_plan:
        day = item["day"]
        duration = item["duration_minutes"]

        if duration <= 0 or duration > 90:
            raise ValueError("Invalid study session duration.")

        daily_totals[day] = daily_totals.get(day, 0) + duration

    for total in daily_totals.values():
        if total > available_minutes:
            raise ValueError("Daily study time limit exceeded.")

    actions = [
        {
            "type": "study_plan",
            "start_date": start_date.isoformat(),
            "horizon_days": horizon_days,
            "available_minutes_per_day": available_minutes,
            "sessions": generated_plan,
        },
        {
            "type": "recommendation",
            "message": recommendation["recommendation"],
            "reasons": recommendation["reasons"],
        },
        {
            "type": "deadline_risks",
            "risks": deadline_risks,
        },
    ]

    requires_confirmation = (
        approval_mode == "ask_before_changes"
    )

    return {
        "summary": (
            f"Generated a proposed {horizon_days}-day study plan "
            f"with {available_minutes} available minutes per day. "
            f"{len(generated_plan)} study sessions were scheduled."
        ),
        "actions": actions,
        "requires_confirmation": requires_confirmation,
    }