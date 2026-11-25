"""
Planning API Router.

Connects authenticated student data, subjects, topics,
priority calculation, scheduling and database persistence.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session

from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user

from app.modules.students.models import Student
from app.modules.subjects.models import Subject
from app.modules.topics.models import Topic

from app.modules.planning.schemas import (
    PlanRequest,
    PlannedSession
)

from app.modules.planning.preferred_time_models import (
    PreferredStudyTime
)

from app.modules.planning.preferred_time_schemas import (
    PreferredStudyTimeCreate,
    PreferredStudyTimeRead,
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
# 1. VERIFY STUDENT OWNERSHIP
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
            detail="Student not found."
        )

    return student


# ==================================================
# 2. GENERATE STUDY PLAN
# ==================================================

@router.post(
    "/generate",
    response_model=list[PlannedSession]
)
def generate(
    request: PlanRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    # VERIFY STUDENT OWNERSHIP

    get_owned_student(
        request.student_id,
        current_user,
        session
    )

    # GET EXISTING PLANNING SETTINGS

    existing_settings = get_plan_settings(
        session,
        request.student_id
    )

    start_date = (
        existing_settings.plan_start
        if existing_settings
        else date.today()
    )

    # RETRIEVE STUDENT TOPICS

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

    # PREPARE TOPIC INFORMATION

    topics = []

    for topic, subject in results:

        try:
            exam_date = (
                subject.exam_date
                if isinstance(subject.exam_date, date)
                else date.fromisoformat(subject.exam_date)
            )

            if exam_date is None:
                raise ValueError("Missing exam date")

        except (ValueError, TypeError):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid exam date for {subject.name}."
            )

        topics.append({

            "id": topic.id,

            "name": topic.name,

            "estimated_minutes": topic.estimated_minutes,

            "difficulty": topic.difficulty,

            "completion_percent": topic.completion_percent,

            "confidence": topic.confidence,

            "priority": topic.priority,

            "days_to_exam": (
                exam_date - start_date
            ).days,

            "exam_weight": subject.exam_weight

        })

    # RETRIEVE SAVED PREFERRED TIMES

    preferred_times = session.exec(
        select(PreferredStudyTime)
        .where(
            PreferredStudyTime.student_id == request.student_id
        )
    ).all()

    # GENERATE STUDY SCHEDULE

    try:

        generated_plan = generate_plan(
            topics=topics,
            available_minutes=request.available_minutes_per_day,
            days=request.horizon_days,
            start_date=start_date,
            preferred_times=preferred_times
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

    # SAVE PLANNING SETTINGS

    save_plan_settings(
        session=session,
        student_id=request.student_id,
        start=start_date,
        days=request.horizon_days
    )

    # SAVE GENERATED SESSIONS

    try:

        persist_generated_sessions(
            session=session,
            student_id=request.student_id,
            generated_plan=generated_plan,
            start_date=start_date,
            days=request.horizon_days
        )

    except Exception:

        session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save generated study sessions."
        )

    return generated_plan


# ==================================================
# 3. PREFERRED STUDY TIME MANAGEMENT
# ==================================================


# GET PREFERRED STUDY TIMES

@router.get(
    "/preferred-times/",
    response_model=list[PreferredStudyTimeRead]
)
def get_preferred_times(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    get_owned_student(
        student_id,
        current_user,
        session
    )

    statement = (
        select(PreferredStudyTime)
        .where(
            PreferredStudyTime.student_id == student_id
        )
        .order_by(
            PreferredStudyTime.day_of_week,
            PreferredStudyTime.start_time
        )
    )

    return session.exec(statement).all()


# ==================================================
# 4. CREATE PREFERRED STUDY TIME
# ==================================================

@router.post(
    "/preferred-times/",
    response_model=PreferredStudyTimeRead
)
def create_preferred_time(
    preferred_time: PreferredStudyTimeCreate,
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    get_owned_student(
        student_id,
        current_user,
        session
    )

    if preferred_time.start_time >= preferred_time.end_time:

        raise HTTPException(
            status_code=400,
            detail="End time must be later than start time."
        )

    new_preferred_time = PreferredStudyTime(

        student_id=student_id,

        day_of_week=preferred_time.day_of_week,

        start_time=preferred_time.start_time,

        end_time=preferred_time.end_time,

    )

    session.add(new_preferred_time)

    session.commit()

    session.refresh(new_preferred_time)

    return new_preferred_time


# ==================================================
# 5. DELETE PREFERRED STUDY TIME
# ==================================================

@router.delete(
    "/preferred-times/{time_id}"
)
def delete_preferred_time(
    time_id: int,
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    get_owned_student(
        student_id,
        current_user,
        session
    )

    preferred_time = session.exec(
        select(PreferredStudyTime)
        .where(
            PreferredStudyTime.id == time_id
        )
        .where(
            PreferredStudyTime.student_id == student_id
        )
    ).first()

    if preferred_time is None:

        raise HTTPException(
            status_code=404,
            detail="Preferred study time not found."
        )

    session.delete(preferred_time)

    session.commit()

    return {
        "message": "Preferred study time deleted successfully."
    }