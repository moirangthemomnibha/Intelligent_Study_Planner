"""
Planning API Router.

Connects student data, subjects, topics,
priority calculation, scheduling and database persistence.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session

from app.modules.students.models import Student
from app.modules.subjects.models import Subject
from app.modules.topics.models import Topic

from app.modules.planning.schemas import (
    PlanRequest,
    PlannedSession
)

from app.modules.planning.service import (
    generate_plan,
    get_plan_settings,
    save_plan_settings,
    persist_generated_sessions
)


router = APIRouter(
    prefix="/planning",
    tags=["Planning"]
)


# ==================================================
# GENERATE STUDY PLAN
# ==================================================

@router.post(
    "/generate",
    response_model=list[PlannedSession]
)
def generate(
    request: PlanRequest,
    session: Session = Depends(get_session)
):
    """
    Generate and persist a personalized study plan.
    """

    # ------------------------------------------
    # 1. VERIFY STUDENT
    # ------------------------------------------

    student = session.get(
        Student,
        request.student_id
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # ------------------------------------------
    # 2. DETERMINE PLAN START DATE
    # ------------------------------------------

    existing_settings = get_plan_settings(
        session,
        request.student_id
    )

    if existing_settings:

        start_date = existing_settings.plan_start

    else:

        start_date = date.today()

    # ------------------------------------------
    # 3. RETRIEVE STUDENT TOPICS
    # ------------------------------------------

    statement = (
        select(Topic, Subject)
        .join(
            Subject,
            Topic.subject_id == Subject.id
        )
        .where(
            Subject.student_id == request.student_id
        )
        .order_by(Topic.id)
    )

    results = session.exec(statement).all()

    if not results:

        raise HTTPException(
            status_code=400,
            detail="No topics found. Add subjects and topics first."
        )

    topics = []

    # ------------------------------------------
    # 4. PREPARE TOPIC INFORMATION
    # ------------------------------------------

    for topic, subject in results:

        try:

            exam_date = date.fromisoformat(
                subject.exam_date
            )

        except ValueError:

            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid exam date for subject "
                    f"'{subject.name}'. Use YYYY-MM-DD."
                )
            )

        days_to_exam = (
            exam_date - start_date
        ).days

        topics.append({

            "id": topic.id,

            "name": topic.name,

            "estimated_minutes": topic.estimated_minutes,

            "difficulty": topic.difficulty,

            "completion_percent": topic.completion_percent,

            "confidence": topic.confidence,

            "priority": topic.priority,

            "days_to_exam": days_to_exam,

            "exam_weight": subject.exam_weight

        })

    # ------------------------------------------
    # 5. GENERATE STUDY SCHEDULE
    # ------------------------------------------

    try:

        generated_plan = generate_plan(
            topics=topics,
            available_minutes=request.available_minutes_per_day,
            days=request.horizon_days,
            start_date=start_date
        )

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    if not generated_plan:

        raise HTTPException(
            status_code=400,
            detail="No study sessions could be generated."
        )

    # ------------------------------------------
    # 6. SAVE PLANNING SETTINGS
    # ------------------------------------------

    save_plan_settings(
        session=session,
        student_id=request.student_id,
        start=start_date,
        days=request.horizon_days
    )

    # ------------------------------------------
    # 7. PERSIST GENERATED SESSIONS
    # ------------------------------------------

    try:

        persist_generated_sessions(
            session=session,
            student_id=request.student_id,
            generated_plan=generated_plan,
            start_date=start_date,
            days=request.horizon_days
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Failed to save generated study sessions."
        )

    # ------------------------------------------
    # 8. RETURN GENERATED PLAN
    # ------------------------------------------

    return generated_plan