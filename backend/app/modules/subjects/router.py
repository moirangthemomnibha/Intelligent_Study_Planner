"""HTTP endpoints for managing student subjects."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user
from app.modules.subjects.models import Subject
from app.modules.students.models import Student

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


# ==========================================
# VERIFY STUDENT OWNERSHIP
# ==========================================

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

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    return student


# ==========================================
# VERIFY SUBJECT OWNERSHIP
# ==========================================

def get_owned_subject(
    subject_id: int,
    current_user: User,
    session: Session,
):
    subject = session.get(Subject, subject_id)

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found."
        )

    get_owned_student(
        subject.student_id,
        current_user,
        session
    )

    return subject


# ==========================================
# CREATE SUBJECT
# ==========================================

@router.post("/", response_model=Subject)
def create_subject(
    subject: Subject,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a subject for the authenticated student."""

    get_owned_student(
        subject.student_id,
        current_user,
        session
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Retrieve subjects belonging to the authenticated student."""

    get_owned_student(
        student_id,
        current_user,
        session
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return get_owned_subject(
        subject_id,
        current_user,
        session
    )


# ==========================================
# DELETE SUBJECT
# ==========================================

@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    subject = get_owned_subject(
        subject_id,
        current_user,
        session
    )

    session.delete(subject)
    session.commit()

    return {
        "message": "Subject deleted successfully."
    }