"""HTTP endpoints for managing student subjects."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session
from app.modules.subjects.models import Subject
from app.modules.students.models import Student

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


# ==========================================
# CREATE SUBJECT
# ==========================================

@router.post("/", response_model=Subject)
def create_subject(
    subject: Subject,
    session: Session = Depends(get_session)
):
    """Create a subject for an existing student."""

    student = session.get(Student, subject.student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    subject.id = None

    session.add(subject)
    session.commit()
    session.refresh(subject)

    return subject


# ==========================================
# GET ALL SUBJECTS
# ==========================================

@router.get("/", response_model=list[Subject])
def get_subjects(
    student_id: int,
    session: Session = Depends(get_session)
):
    """Retrieve subjects belonging to a student."""

    student = session.get(Student, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    statement = select(Subject).where(
        Subject.student_id == student_id
    )

    return session.exec(statement).all()


# ==========================================
# GET SUBJECT BY ID
# ==========================================

@router.get("/{subject_id}", response_model=Subject)
def get_subject(
    subject_id: int,
    session: Session = Depends(get_session)
):
    subject = session.get(Subject, subject_id)

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    return subject


# ==========================================
# DELETE SUBJECT
# ==========================================

@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    session: Session = Depends(get_session)
):
    subject = session.get(Subject, subject_id)

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    session.delete(subject)
    session.commit()

    return {
        "message": "Subject deleted successfully"
    }