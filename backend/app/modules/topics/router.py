"""
HTTP endpoints for managing student topics.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session

from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user

from app.modules.students.models import Student
from app.modules.topics.models import Topic
from app.modules.subjects.models import Subject
from app.modules.sessions.models import StudySession


router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)


# ==================================================
# VERIFY SUBJECT OWNERSHIP
# ==================================================

def get_owned_subject(
    subject_id: int,
    current_user: User,
    session: Session,
):
    subject = session.get(Subject, subject_id)

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found."
        )

    student = session.exec(
        select(Student)
        .where(Student.id == subject.student_id)
        .where(Student.user_id == current_user.id)
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found."
        )

    return subject


# ==================================================
# VERIFY TOPIC OWNERSHIP
# ==================================================

def get_owned_topic(
    topic_id: int,
    current_user: User,
    session: Session,
):
    topic = session.get(Topic, topic_id)

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found."
        )

    get_owned_subject(
        topic.subject_id,
        current_user,
        session
    )

    return topic


# ==================================================
# 1. CREATE TOPIC
# ==================================================

@router.post("/", response_model=Topic)
def create_topic(
    topic: Topic,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a topic under a subject belonging to the authenticated user.
    """

    get_owned_subject(
        topic.subject_id,
        current_user,
        session
    )

    topic.id = None

    session.add(topic)
    session.commit()
    session.refresh(topic)

    return topic


# ==================================================
# 2. GET TOPICS BY SUBJECT
# ==================================================

@router.get("/", response_model=list[Topic])
def get_topics(
    subject_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve topics belonging to the authenticated user's subject.
    """

    get_owned_subject(
        subject_id,
        current_user,
        session
    )

    statement = select(Topic).where(
        Topic.subject_id == subject_id
    )

    return session.exec(statement).all()


# ==================================================
# 3. GET TOPIC BY ID
# ==================================================

@router.get("/{topic_id}", response_model=Topic)
def get_topic(
    topic_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve an individual topic belonging to the authenticated user.
    """

    return get_owned_topic(
        topic_id,
        current_user,
        session
    )


# ==================================================
# 4. UPDATE TOPIC
# ==================================================

@router.put("/{topic_id}", response_model=Topic)
def update_topic(
    topic_id: int,
    updated_topic: Topic,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Update a topic belonging to the authenticated user.
    """

    topic = get_owned_topic(
        topic_id,
        current_user,
        session
    )

    # Verify that the destination subject also belongs to this user.
    get_owned_subject(
        updated_topic.subject_id,
        current_user,
        session
    )

    topic.subject_id = updated_topic.subject_id
    topic.name = updated_topic.name
    topic.estimated_minutes = updated_topic.estimated_minutes
    topic.difficulty = updated_topic.difficulty
    topic.completion_percent = updated_topic.completion_percent
    topic.confidence = updated_topic.confidence
    topic.priority = updated_topic.priority

    session.add(topic)
    session.commit()
    session.refresh(topic)

    return topic


# ==================================================
# 5. DELETE TOPIC
# ==================================================

@router.delete("/{topic_id}")
def delete_topic(
    topic_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an owned topic only if it has no existing study sessions.
    """

    topic = get_owned_topic(
        topic_id,
        current_user,
        session
    )

    existing_sessions = session.exec(
        select(StudySession).where(
            StudySession.topic_id == topic_id
        )
    ).first()

    if existing_sessions:
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete this topic because "
                "study sessions already exist."
            )
        )

    session.delete(topic)
    session.commit()

    return {
        "message": "Topic deleted successfully."
    }