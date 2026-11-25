"""
HTTP endpoints for AI-based study recommendations.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.session import get_session

from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user

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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # ==========================================
    # 1. VERIFY STUDENT OWNERSHIP
    # ==========================================

    student = session.exec(
        select(Student)
        .where(Student.id == request.student_id)
        .where(Student.user_id == current_user.id)
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    # ==========================================
    # 2. RETRIEVE THE STUDENT'S TOPICS
    # ==========================================

    statement = (
        select(Topic, Subject)
        .join(Subject, Topic.subject_id == Subject.id)
        .where(Subject.student_id == student.id)
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

    # ==========================================
    # 3. PREPARE STUDENT INFORMATION
    # ==========================================

    student_summary = {
        "student_id": student.id,
        "topics": student_topics,
    }

    # ==========================================
    # 4. GENERATE RECOMMENDATION
    # ==========================================

    result = recommend_next_action(student_summary)

    return RecommendationResponse(**result)