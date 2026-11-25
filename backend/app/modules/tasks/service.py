from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, select

from .models import Task
from .schemas import TaskCreate, TaskUpdate
from app.modules.subjects.models import Subject
from app.modules.topics.models import Topic


def validate_task_links(
    session: Session,
    student_id: int,
    subject_id: int | None,
    topic_id: int | None,
):
    subject = None

    if subject_id is not None:
        subject = session.get(Subject, subject_id)

        if not subject or subject.student_id != student_id:
            raise HTTPException(status_code=404, detail="Subject not found")

    if topic_id is not None:
        topic = session.get(Topic, topic_id)

        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        topic_subject = session.get(Subject, topic.subject_id)

        if not topic_subject or topic_subject.student_id != student_id:
            raise HTTPException(status_code=404, detail="Topic not found")

        if subject_id is not None and topic.subject_id != subject_id:
            raise HTTPException(
                status_code=400,
                detail="Topic does not belong to the selected subject",
            )


def create_task(
    session: Session,
    task_data: TaskCreate,
):
    validate_task_links(
        session,
        task_data.student_id,
        task_data.subject_id,
        task_data.topic_id,
    )

    task = Task(**task_data.model_dump())

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def get_tasks(
    session: Session,
    student_id: int,
):
    statement = (
        select(Task)
        .where(Task.student_id == student_id)
        .order_by(Task.created_at.desc())
    )

    return session.exec(statement).all()


def get_task(
    session: Session,
    task_id: int,
    student_id: int,
):
    task = session.get(Task, task_id)

    if not task or task.student_id != student_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


def update_task(
    session: Session,
    task_id: int,
    student_id: int,
    task_data: TaskUpdate,
):
    task = get_task(session, task_id, student_id)

    updates = task_data.model_dump(exclude_unset=True)

    subject_id = updates.get("subject_id", task.subject_id)
    topic_id = updates.get("topic_id", task.topic_id)

    validate_task_links(
        session,
        student_id,
        subject_id,
        topic_id,
    )

    for key, value in updates.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(
    session: Session,
    task_id: int,
    student_id: int,
):
    task = get_task(session, task_id, student_id)

    session.delete(task)
    session.commit()

    return {"message": "Task deleted successfully"}