from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session
from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user
from app.modules.students.models import Student

from app.modules.students.schemas import (
    StudentCreate,
    StudentRead,
    StudentProfileUpdate,
    StudentProfileRead,
)

from app.modules.students.service import (
    create_student,
    update_profile,
    remove_profile_picture,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentRead)
def add_student(
    data: StudentCreate,
    session: Session = Depends(get_session),
):
    try:
        return create_student(session, data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


def get_authenticated_student(
    user: User,
    session: Session,
):
    student = session.exec(
        select(Student).where(Student.user_id == user.id)
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found.",
        )

    return student


@router.get("/profile", response_model=StudentProfileRead)
def read_student_profile(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return get_authenticated_student(current_user, session)


@router.put("/profile", response_model=StudentProfileRead)
def edit_student_profile(
    data: StudentProfileUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    student = get_authenticated_student(current_user, session)

    updated = update_profile(session, student.id, data)

    if not updated:
        raise HTTPException(status_code=404, detail="Student not found.")

    return updated


@router.delete("/profile-picture")
def delete_student_profile_picture(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    student = get_authenticated_student(current_user, session)

    removed = remove_profile_picture(session, student.id)

    if not removed:
        raise HTTPException(status_code=404, detail="Student not found.")

    return {"message": "Profile picture removed successfully."}