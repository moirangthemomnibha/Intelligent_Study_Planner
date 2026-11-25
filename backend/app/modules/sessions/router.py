"""
HTTP endpoints for managing study sessions.
"""

from datetime import date, datetime, timedelta, timezone
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session

from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user

from app.modules.sessions.models import StudySession
from app.modules.students.models import Student


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


# ==================================================
# VERIFY SESSION OWNERSHIP
# ==================================================

def get_owned_session(
    session_id: int,
    current_user: User,
    session: Session,
):
    """
    Retrieve a study session only if it belongs
    to the authenticated user.
    """

    study_session = session.get(
        StudySession,
        session_id
    )

    if study_session is None:
        raise HTTPException(
            status_code=404,
            detail="Study session not found."
        )

    student = session.exec(
        select(Student)
        .where(Student.id == study_session.student_id)
        .where(Student.user_id == current_user.id)
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Study session not found."
        )

    return study_session


# ==================================================
# 1. GET ALL STUDENT SESSIONS
# ==================================================

@router.get("/", response_model=list[StudySession])
def get_sessions(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Retrieve sessions belonging to the authenticated student."""

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

    statement = (
        select(StudySession)
        .where(StudySession.student_id == student_id)
        .order_by(StudySession.planned_date)
    )

    return session.exec(statement).all()

# ==================================================
# 2. WEEKLY STUDY REPORT
# ==================================================

@router.get("/weekly-report")
def get_weekly_report(
    student_id: int,
    week_start: date = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Verify student ownership
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

    # Determine week
    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=6)

    # Retrieve weekly sessions
    sessions = session.exec(
        select(StudySession)
        .where(StudySession.student_id == student_id)
        .where(StudySession.planned_date >= week_start)
        .where(StudySession.planned_date <= week_end)
    ).all()

    daily_report = []

    total_planned = 0
    total_actual = 0
    completed_sessions = 0

    for i in range(7):
        current_day = week_start + timedelta(days=i)

        day_sessions = [
            s for s in sessions
            if s.planned_date == current_day.isoformat()
        ]

        planned = sum(s.planned_minutes for s in day_sessions)
        actual = sum(s.actual_minutes or 0 for s in day_sessions)

        total_planned += planned
        total_actual += actual

        completed_sessions += sum(
            1 for s in day_sessions
            if s.status == "completed"
        )

        daily_report.append({
            "date": current_day.isoformat(),
            "planned_minutes": planned,
            "actual_minutes": actual,
            "sessions": len(day_sessions)
        })

    total_sessions = len(sessions)

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "total_planned_minutes": total_planned,
        "total_actual_minutes": total_actual,
        "total_actual_hours": round(total_actual / 60, 2),
        "completed_sessions": completed_sessions,
        "total_sessions": total_sessions,
        "weekly_progress": round(
            completed_sessions / total_sessions * 100, 2
        ) if total_sessions else 0,
        "daily_report": daily_report
    }

# ==================================================
# 3. GET SESSION BY ID
# ==================================================

@router.get("/{session_id}", response_model=StudySession)
def get_session_by_id(
    session_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Retrieve an individual owned study session."""

    return get_owned_session(
        session_id,
        current_user,
        session
    )


# ==================================================
# 4. UPDATE SESSION STATUS
# ==================================================

@router.patch("/{session_id}/status")
def update_session_status(
    session_id: int,
    status: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update the status of an owned study session."""

    allowed_statuses = {
        "planned",
        "completed",
        "missed",
        "partial"
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid session status."
        )

    study_session = get_owned_session(
        session_id,
        current_user,
        session
    )

    study_session.status = status

    session.add(study_session)
    session.commit()
    session.refresh(study_session)

    return study_session


# ==================================================
# 5. RECORD ACTUAL STUDY TIME
# ==================================================

@router.patch("/{session_id}/progress")
def update_session_progress(
    session_id: int,
    actual_minutes: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Record actual study time for an owned session."""

    if actual_minutes < 0:
        raise HTTPException(
            status_code=422,
            detail="Actual study minutes cannot be negative."
        )

    study_session = get_owned_session(
        session_id,
        current_user,
        session
    )

    study_session.actual_minutes = actual_minutes
    study_session.updated_at = datetime.now(timezone.utc)

    if actual_minutes == 0:
        study_session.status = "missed"
        study_session.completed_at = None

    elif actual_minutes >= study_session.planned_minutes:
        study_session.status = "completed"
        study_session.completed_at = datetime.now(timezone.utc)

    else:
        study_session.status = "partial"
        study_session.completed_at = None

    session.add(study_session)
    session.commit()
    session.refresh(study_session)

    return study_session


# ==================================================
# 6. ADD SESSION REFLECTION
# ==================================================

@router.patch("/{session_id}/reflection")
def update_session_reflection(
    session_id: int,
    reflection: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Save a reflection for an owned study session."""

    study_session = get_owned_session(
        session_id,
        current_user,
        session
    )

    study_session.reflection = reflection

    session.add(study_session)
    session.commit()
    session.refresh(study_session)

    return study_session