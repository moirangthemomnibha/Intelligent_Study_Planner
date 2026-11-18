"""
HTTP endpoints for managing study sessions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session

from app.modules.sessions.models import StudySession
from app.modules.students.models import Student
from app.modules.topics.models import Topic


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


# ==================================================
# 1. GET ALL STUDENT SESSIONS
# ==================================================

@router.get("/", response_model=list[StudySession])
def get_sessions(
    student_id: int,
    session: Session = Depends(get_session)
):
    """Retrieve all study sessions belonging to a student."""

    student = session.get(Student, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    statement = (
        select(StudySession)
        .where(StudySession.student_id == student_id)
        .order_by(StudySession.planned_date)
    )

    return session.exec(statement).all()


# ==================================================
# 2. GET SESSION BY ID
# ==================================================

@router.get("/{session_id}", response_model=StudySession)
def get_session_by_id(
    session_id: int,
    session: Session = Depends(get_session)
):
    """Retrieve an individual study session."""

    study_session = session.get(
        StudySession,
        session_id
    )

    if study_session is None:
        raise HTTPException(
            status_code=404,
            detail="Study session not found"
        )

    return study_session


# ==================================================
# 3. UPDATE SESSION STATUS
# ==================================================

@router.patch("/{session_id}/status")
def update_session_status(
    session_id: int,
    status: str,
    session: Session = Depends(get_session)
):
    """Update the status of a study session."""

    allowed_statuses = {
        "planned",
        "completed",
        "missed",
        "partial"
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid session status"
        )

    study_session = session.get(
        StudySession,
        session_id
    )

    if study_session is None:
        raise HTTPException(
            status_code=404,
            detail="Study session not found"
        )

    study_session.status = status

    session.add(study_session)
    session.commit()
    session.refresh(study_session)

    return study_session


# ==================================================
# 4. RECORD ACTUAL STUDY TIME
# ==================================================

@router.patch("/{session_id}/progress")
def update_session_progress(
    session_id: int,
    actual_minutes: int,
    session: Session = Depends(get_session)
):
    """Record the actual time spent studying."""

    if actual_minutes < 0:
        raise HTTPException(
            status_code=422,
            detail="Actual study minutes cannot be negative"
        )

    study_session = session.get(
        StudySession,
        session_id
    )

    if study_session is None:
        raise HTTPException(
            status_code=404,
            detail="Study session not found"
        )

    study_session.actual_minutes = actual_minutes

    if actual_minutes == 0:
        study_session.status = "missed"

    elif actual_minutes >= study_session.planned_minutes:
        study_session.status = "completed"

    else:
        study_session.status = "partial"

    session.add(study_session)
    session.commit()
    session.refresh(study_session)

    return study_session


# ==================================================
# 5. ADD SESSION REFLECTION
# ==================================================

@router.patch("/{session_id}/reflection")
def update_session_reflection(
    session_id: int,
    reflection: str,
    session: Session = Depends(get_session)
):
    """Save a student's reflection after studying."""

    study_session = session.get(
        StudySession,
        session_id
    )

    if study_session is None:
        raise HTTPException(
            status_code=404,
            detail="Study session not found"
        )

    study_session.reflection = reflection

    session.add(study_session)
    session.commit()
    session.refresh(study_session)

    return study_session