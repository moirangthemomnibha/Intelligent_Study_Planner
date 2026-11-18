"""
HTTP endpoints for AI-based study recommendations.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session
from app.modules.students.models import Student
from app.modules.subjects.models import Subject
from app.modules.topics.models import Topic

from app.modules.ai.schemas import (
    RecommendationRequest,
    RecommendationResponse,
)

from app.modules.ai.service import recommend_next_action


router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/recommend",
    response_model=RecommendationResponse
)
def get_recommendation(
    request: RecommendationRequest,
    session: Session = Depends(get_session)
):
    # Check whether the student exists.
    student = session.get(Student, request.student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    # Retrieve the student's topics and associated subjects.
    statement = (
        select(Topic, Subject)
        .join(Subject, Topic.subject_id == Subject.id)
        .where(Subject.student_id == request.student_id)
    )

    results = session.exec(statement).all()

    student_topics = []

    for topic, subject in results:

        try:
            exam_date = date.fromisoformat(subject.exam_date)
            days_to_exam = (exam_date - date.today()).days
        except (ValueError, TypeError):
            days_to_exam = 30

        student_topics.append({
            "id": topic.id,
            "name": topic.name,
            "estimated_minutes": topic.estimated_minutes,
            "difficulty": topic.difficulty,
            "completion_percent": topic.completion_percent,
            "confidence": topic.confidence,
            "priority": topic.priority,
            "exam_weight": subject.exam_weight,
            "days_to_exam": days_to_exam,
        })

    # Prepare student information for the recommendation engine.
    student_summary = {
        "student_id": student.id,
        "topics": student_topics,
    }

    # Generate the recommendation.
    result = recommend_next_action(student_summary)

    return RecommendationResponse(**result)