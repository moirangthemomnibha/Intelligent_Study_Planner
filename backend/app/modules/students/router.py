from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database.session import get_session
from app.modules.students.schemas import (
    StudentCreate,
    StudentRead,
    StudentProfileUpdate,
    StudentProfileRead,
)
from app.modules.students.service import (
    create_student,
    get_profile,
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


@router.get("/{student_id}/profile", response_model=StudentProfileRead)
def read_student_profile(
    student_id: int,
    session: Session = Depends(get_session),
):
    student = get_profile(session, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.put("/{student_id}/profile", response_model=StudentProfileRead)
def edit_student_profile(
    student_id: int,
    data: StudentProfileUpdate,
    session: Session = Depends(get_session),
):
    student = update_profile(session, student_id, data)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.delete("/{student_id}/profile-picture")
def delete_student_profile_picture(
    student_id: int,
    session: Session = Depends(get_session),
):
    student = remove_profile_picture(session, student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Profile picture removed successfully"}