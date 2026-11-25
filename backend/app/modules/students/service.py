"""Create, read, and update student profiles."""

from sqlmodel import Session, select

from app.modules.students.models import Student
from app.modules.students.schemas import (
    StudentCreate,
    StudentProfileUpdate,
)


def create_student(session: Session, data: StudentCreate):
    existing = session.exec(
        select(Student).where(Student.email == data.email)
    ).first()

    if existing:
        raise ValueError("A profile with this email already exists")

    student = Student(**data.model_dump())

    session.add(student)
    session.commit()
    session.refresh(student)

    return student


def get_profile(session: Session, student_id: int):
    return session.exec(
        select(Student).where(Student.id == student_id)
    ).first()


def update_profile(
    session: Session,
    student_id: int,
    data: StudentProfileUpdate,
):
    student = get_profile(session, student_id)

    if not student:
        return None

    profile_data = data.model_dump(exclude_unset=True)

    for field, value in profile_data.items():
        setattr(student, field, value)

    session.add(student)
    session.commit()
    session.refresh(student)

    return student


def remove_profile_picture(session: Session, student_id: int):
    student = get_profile(session, student_id)

    if not student:
        return None

    student.profile_picture_url = None

    session.add(student)
    session.commit()
    session.refresh(student)

    return student