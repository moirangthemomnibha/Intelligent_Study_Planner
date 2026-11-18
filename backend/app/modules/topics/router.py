"""
HTTP endpoints for managing student topics.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session

from app.modules.topics.models import Topic
from app.modules.subjects.models import Subject
from app.modules.sessions.models import StudySession


router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)


# ==================================================
# 1. CREATE TOPIC
# ==================================================

@router.post("/", response_model=Topic)
def create_topic(
    topic: Topic,
    session: Session = Depends(get_session)
):
    """
    Create a topic under an existing subject.
    """

    subject = session.get(
        Subject,
        topic.subject_id
    )

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
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
    session: Session = Depends(get_session)
):
    """
    Retrieve all topics belonging to a subject.
    """

    subject = session.get(
        Subject,
        subject_id
    )

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
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
    session: Session = Depends(get_session)
):
    """
    Retrieve an individual topic.
    """

    topic = session.get(
        Topic,
        topic_id
    )

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found"
        )

    return topic


# ==================================================
# 4. UPDATE TOPIC
# ==================================================

@router.put("/{topic_id}", response_model=Topic)
def update_topic(
    topic_id: int,
    updated_topic: Topic,
    session: Session = Depends(get_session)
):
    """
    Update an existing topic.
    """

    topic = session.get(
        Topic,
        topic_id
    )

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found"
        )

    subject = session.get(
        Subject,
        updated_topic.subject_id
    )

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
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
    session: Session = Depends(get_session)
):
    """
    Delete a topic if it has no existing study sessions.
    """

    topic = session.get(
        Topic,
        topic_id
    )

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found"
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
        "message": "Topic deleted successfully"
    }