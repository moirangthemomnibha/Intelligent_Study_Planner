"""HTTP endpoints for the study planning agent."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session

from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user

from app.modules.students.models import Student
from app.modules.subjects.models import Subject
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


# ==================================================
# VERIFY STUDENT OWNERSHIP
# ==================================================

def get_owned_student(
    student_id: int,
    current_user: User,
    session: Session,
):
    student = session.exec(
        select(Student)
        .where(Student.id == student_id)
        .where(Student.user_id == current_user.id)
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return student


# ==================================================
# 1. RUN STUDY AGENT
# ==================================================

@router.post("/run", response_model=AgentProposal)
def run_study_agent(
    request: AgentRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Verify that the requested student belongs to the logged-in user.
    get_owned_student(
        request.student_id,
        current_user,
        session,
    )

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


# ==================================================
# 2. CONFIRM AND SAVE STUDY PLAN
# ==================================================

@router.post("/confirm")
def confirm_study_plan(
    request: AgentConfirmRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # ------------------------------------------
    # VERIFY STUDENT OWNERSHIP
    # ------------------------------------------

    get_owned_student(
        request.student_id,
        current_user,
        session,
    )

    # ------------------------------------------
    # VERIFY TOPIC OWNERSHIP
    # ------------------------------------------

    owned_topics = session.exec(
        select(Topic)
        .join(
            Subject,
            Topic.subject_id == Subject.id,
        )
        .where(
            Subject.student_id == request.student_id
        )
    ).all()

    owned_topic_ids = {
        topic.id for topic in owned_topics
    }

    # ------------------------------------------
    # VALIDATE PROPOSED STUDY SESSIONS
    # ------------------------------------------

    if request.horizon_days < 1 or request.horizon_days > 30:
        raise HTTPException(
            status_code=400,
            detail="Planning period must be between 1 and 30 days.",
        )

    if request.available_minutes_per_day <= 0:
        raise HTTPException(
            status_code=400,
            detail="Available study time must be greater than zero.",
        )

    if not request.generated_plan:
        raise HTTPException(
            status_code=400,
            detail="The proposed study plan is empty.",
        )

    daily_totals = {}

    end_date = request.start_date + timedelta(
        days=request.horizon_days - 1
    )

    for item in request.generated_plan:

        topic_id = item.get("topic_id")
        day = item.get("day")
        duration = item.get("duration_minutes")

        # Check topic ownership.
        if topic_id not in owned_topic_ids:
            raise HTTPException(
                status_code=400,
                detail="Invalid topic in proposed plan.",
            )

        # Check session duration.
        if (
            not isinstance(duration, int)
            or isinstance(duration, bool)
            or not 1 <= duration <= 90
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid study session duration.",
            )

        # Check study session date.
        try:
            session_day = date.fromisoformat(day)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid study session date.",
            )

        if not request.start_date <= session_day <= end_date:
            raise HTTPException(
                status_code=400,
                detail="Study session is outside the planning period.",
            )

        daily_totals[day] = (
            daily_totals.get(day, 0) + duration
        )

    # ------------------------------------------
    # VERIFY DAILY STUDY TIME
    # ------------------------------------------

    if any(
        total > request.available_minutes_per_day
        for total in daily_totals.values()
    ):
        raise HTTPException(
            status_code=400,
            detail="Daily study time limit exceeded.",
        )

    # ------------------------------------------
    # SAVE APPROVED STUDY PLAN
    # ------------------------------------------

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