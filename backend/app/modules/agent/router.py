"""HTTP endpoints for the study planning agent."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session
from app.modules.students.models import Student
from app.modules.topics.models import Topic

from app.modules.agent.schemas import (
    AgentRequest,
    AgentProposal,
    AgentConfirmRequest,
)

from app.modules.agent.service import run_agent

from app.modules.planning.service import (
    save_plan_settings,
    persist_generated_sessions,
)


router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/run", response_model=AgentProposal)
def run_study_agent(
    request: AgentRequest,
    session: Session = Depends(get_session),
):
    try:
        return run_agent(
            session=session,
            student_id=request.student_id,
            intent=request.intent,
            available_minutes=request.available_minutes_per_day,
            horizon_days=request.horizon_days,
            approval_mode=request.approval_mode,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.post("/confirm")
def confirm_study_plan(
    request: AgentConfirmRequest,
    session: Session = Depends(get_session),
):
    student = session.get(Student, request.student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    # Verify that every topic belongs to this student.
    owned_topics = session.exec(
        select(Topic)
        .join(
            __import__(
                "app.modules.subjects.models",
                fromlist=["Subject"]
            ).Subject,
            Topic.subject_id ==
            __import__(
                "app.modules.subjects.models",
                fromlist=["Subject"]
            ).Subject.id,
        )
        .where(
            __import__(
                "app.modules.subjects.models",
                fromlist=["Subject"]
            ).Subject.student_id == request.student_id
        )
    ).all()

    owned_topic_ids = {topic.id for topic in owned_topics}

    daily_totals = {}

    for item in request.generated_plan:
        topic_id = item.get("topic_id")
        day = item.get("day")
        duration = item.get("duration_minutes")

        if topic_id not in owned_topic_ids:
            raise HTTPException(
                status_code=400,
                detail="Invalid topic in proposed plan.",
            )

        if not isinstance(duration, int) or not 1 <= duration <= 90:
            raise HTTPException(
                status_code=400,
                detail="Invalid study session duration.",
            )

        try:
            from datetime import date, timedelta

            session_day = date.fromisoformat(day)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid study session date.",
            )

        end_date = request.start_date + timedelta(
            days=request.horizon_days - 1
        )

        if not request.start_date <= session_day <= end_date:
            raise HTTPException(
                status_code=400,
                detail="Study session is outside the planning period.",
            )

        daily_totals[day] = daily_totals.get(day, 0) + duration

    if any(
        total > request.available_minutes_per_day
        for total in daily_totals.values()
    ):
        raise HTTPException(
            status_code=400,
            detail="Daily study time limit exceeded.",
        )

    try:
        save_plan_settings(
            session,
            request.student_id,
            request.start_date,
            request.horizon_days,
        )

        saved = persist_generated_sessions(
            session,
            request.student_id,
            request.generated_plan,
            request.start_date,
            request.horizon_days,
        )

        return {
            "message": "Study plan confirmed and saved.",
            "saved_sessions": len(saved),
        }

    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save the study plan.",
        )