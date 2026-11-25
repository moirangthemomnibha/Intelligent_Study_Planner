from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database.session import get_session
from .schemas import TaskCreate, TaskUpdate, TaskRead
from . import service


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
):
    return service.create_task(session, task_data)


@router.get("/", response_model=list[TaskRead])
def get_tasks(
    student_id: int,
    session: Session = Depends(get_session),
):
    return service.get_tasks(session, student_id)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    student_id: int,
    session: Session = Depends(get_session),
):
    return service.get_task(session, task_id, student_id)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    student_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
):
    return service.update_task(
        session,
        task_id,
        student_id,
        task_data,
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    student_id: int,
    session: Session = Depends(get_session),
):
    return service.delete_task(session, task_id, student_id)