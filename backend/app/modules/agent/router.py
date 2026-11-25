"""HTTP endpoints for the study planning agent."""

from datetime import date, timedelta

from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response

from app.database.session import get_session

from app.modules.auth.models import User
from app.modules.auth.dependencies import get_current_user

from app.modules.students.models import Student
from app.modules.subjects.models import Subject
from app.modules.topics.models import Topic

from app.modules.agent.conversation_models import AgentConversation, AgentMessage

from app.modules.agent.schemas import (
    AgentRequest,
    AgentProposal,
    AgentConfirmRequest,
    AgentChatRequest,
    AgentChatResponse,
)

from app.modules.agent.service import (
    run_agent,
    run_chat,
    recover_missed_study_sessions,
    summarize_document,
    generate_quiz,
    generate_flashcards,
    evaluate_student_answer,
    explain_concept,
    translate_text,
    solve_academic_problem,
    generate_revision_notes,
    analyse_learning_progress,
    generate_exam_questions,
    generate_learning_roadmap,
    transcribe_voice_command,
    process_voice_command,
    create_conversation,
    save_conversation_message,
    get_conversation_history,

)


router = APIRouter(prefix="/agent", tags=["Agent"])


# ==================================================
# VERIFY STUDENT OWNERSHIP
# ==================================================

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

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return student


# ==================================================
# 1. RUN STUDY AGENT
# ==================================================

@router.post("/run", response_model=AgentProposal)
async def run_study_agent(
    request: AgentRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Verify that the requested student belongs to the logged-in user.
    get_owned_student(
        request.student_id,
        current_user,
        session,
    )

    try:
        return await run_agent(
            session=session,
            student_id=request.student_id,
            intent=request.intent,
            available_minutes=request.available_minutes_per_day,
            horizon_days=request.horizon_days,
            approval_mode=request.approval_mode,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# ==================================================
# 2. AI CHAT ASSISTANT
# ==================================================

@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(
    request: AgentChatRequest,
    conversation_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(
        request.student_id,
        current_user,
        session,
    )

    conversation = session.get(
        AgentConversation,
        conversation_id,
    )

    try:
        return await run_chat(
            session=session,
            student_id=request.student_id,
            message=request.message,
            conversation_history=request.conversation_history,
            conversation_summary=conversation.summary if conversation else None,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

# ==================================================
# 2. CONFIRM AND SAVE STUDY PLAN
# ==================================================

@router.post("/confirm")
def confirm_study_plan(
    request: AgentConfirmRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # ------------------------------------------
    # VERIFY STUDENT OWNERSHIP
    # ------------------------------------------

    get_owned_student(
        request.student_id,
        current_user,
        session,
    )

    # ------------------------------------------
    # VERIFY TOPIC OWNERSHIP
    # ------------------------------------------

    owned_topics = session.exec(
        select(Topic)
        .join(
            Subject,
            Topic.subject_id == Subject.id,
        )
        .where(
            Subject.student_id == request.student_id
        )
    ).all()

    owned_topic_ids = {
        topic.id for topic in owned_topics
    }

    # ------------------------------------------
    # VALIDATE PROPOSED STUDY SESSIONS
    # ------------------------------------------

    if request.horizon_days < 1 or request.horizon_days > 30:
        raise HTTPException(
            status_code=400,
            detail="Planning period must be between 1 and 30 days.",
        )

    if request.available_minutes_per_day <= 0:
        raise HTTPException(
            status_code=400,
            detail="Available study time must be greater than zero.",
        )

    if not request.generated_plan:
        raise HTTPException(
            status_code=400,
            detail="The proposed study plan is empty.",
        )

    daily_totals = {}

    end_date = request.start_date + timedelta(
        days=request.horizon_days - 1
    )

    for item in request.generated_plan:

        topic_id = item.get("topic_id")
        day = item.get("day")
        duration = item.get("duration_minutes")

        # Check topic ownership.
        if topic_id not in owned_topic_ids:
            raise HTTPException(
                status_code=400,
                detail="Invalid topic in proposed plan.",
            )

        # Check session duration.
        if (
            not isinstance(duration, int)
            or isinstance(duration, bool)
            or not 1 <= duration <= 90
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid study session duration.",
            )

        # Check study session date.
        try:
            session_day = date.fromisoformat(day)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid study session date.",
            )

        if not request.start_date <= session_day <= end_date:
            raise HTTPException(
                status_code=400,
                detail="Study session is outside the planning period.",
            )

        daily_totals[day] = (
            daily_totals.get(day, 0) + duration
        )

    # ------------------------------------------
    # VERIFY DAILY STUDY TIME
    # ------------------------------------------

    if any(
        total > request.available_minutes_per_day
        for total in daily_totals.values()
    ):
        raise HTTPException(
            status_code=400,
            detail="Daily study time limit exceeded.",
        )

    # ------------------------------------------
    # SAVE APPROVED STUDY PLAN
    # ------------------------------------------

    try:
        save_plan_settings(
            session,
            request.student_id,
            request.start_date,
            request.horizon_days,
        )

        saved = persist_generated_sessions(
            session,
            request.student_id,
            request.generated_plan,
            request.start_date,
            request.horizon_days,
        )

        return {
            "message": "Study plan confirmed and saved.",
            "saved_sessions": len(saved),
        }

    except Exception:
        session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to save the study plan.",
        )

@router.post("/recover-missed")
def recover_missed(
    student_id: int,
    available_minutes_per_day: int = 180,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return recover_missed_study_sessions(
            session=session,
            student_id=student_id,
            available_minutes_per_day=available_minutes_per_day,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/upload-document")
async def upload_study_document(
    student_id: int,
    file: UploadFile = File(...),
    summary_type: str = "detailed",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    if summary_type not in {"brief", "detailed", "exam-oriented"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid summary type.",
        )

    try:
        file_bytes = await file.read()

        return await summarize_document(
            filename=file.filename or "",
            file_bytes=file_bytes,
            summary_type=summary_type,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    finally:
        await file.close()

@router.post("/generate-quiz")
async def create_quiz(
    student_id: int,
    topic: str,
    question_count: int = 10,
    difficulty: str = "mixed",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await generate_quiz(
            student_id=student_id,
            topic=topic,
            question_count=question_count,
            difficulty=difficulty,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/generate-flashcards")
async def create_flashcards(
    student_id: int,
    topic: str,
    card_count: int = 10,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await generate_flashcards(
            student_id=student_id,
            topic=topic,
            card_count=card_count,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/generate-flashcards")
async def create_flashcards(
    student_id: int,
    topic: str,
    card_count: int = 10,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await generate_flashcards(
            student_id=student_id,
            topic=topic,
            card_count=card_count,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

@router.post("/evaluate-answer")
async def evaluate_answer(
    student_id: int,
    question: str,
    expected_answer: str,
    student_answer: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await evaluate_student_answer(
            student_id=student_id,
            question=question,
            expected_answer=expected_answer,
            student_answer=student_answer,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/explain-concept")
async def explain_academic_concept(
    student_id: int,
    concept: str,
    level: str = "beginner",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await explain_concept(
            student_id=student_id,
            concept=concept,
            level=level,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/translate")
async def translate_academic_text(
    student_id: int,
    text: str,
    target_language: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await translate_text(
            student_id=student_id,
            text=text,
            target_language=target_language,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/solve-problem")
async def solve_problem(
    student_id: int,
    problem: str,
    subject: str = "general",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await solve_academic_problem(
            student_id=student_id,
            problem=problem,
            subject=subject,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/generate-revision-notes")
async def create_revision_notes(
    student_id: int,
    topic: str,
    note_type: str = "exam-oriented",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await generate_revision_notes(
            student_id=student_id,
            topic=topic,
            note_type=note_type,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/learning-analysis")
async def get_learning_analysis(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await analyse_learning_progress(
            session=session,
            student_id=student_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/generate-exam-questions")
async def create_exam_questions(
    student_id: int,
    topic: str,
    question_count: int = 10,
    question_type: str = "mixed",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await generate_exam_questions(
            student_id=student_id,
            topic=topic,
            question_count=question_count,
            question_type=question_type,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/learning-roadmap")
async def create_learning_roadmap(
    student_id: int,
    subject: str,
    goal: str,
    duration_days: int = 30,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await generate_learning_roadmap(
            student_id=student_id,
            subject=subject,
            goal=goal,
            duration_days=duration_days,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/voice/transcribe")
async def transcribe_voice(
    student_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        audio_bytes = await file.read()

        return await transcribe_voice_command(
            audio_bytes=audio_bytes,
            filename=file.filename or "",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    finally:
        await file.close()

@router.post("/voice/command")
async def execute_voice_command(
    student_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        audio_bytes = await file.read()

        return await process_voice_command(
            session=session,
            student_id=student_id,
            audio_bytes=audio_bytes,
            filename=file.filename or "",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    finally:
        await file.close()

@router.post("/voice/speak")
async def speak_response(
    student_id: int,
    text: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        audio = await generate_voice_response(text)

        return Response(
            content=audio,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=study_response.mp3"
            },
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/document/ask")
async def question_about_document(
    student_id: int,
    question: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        file_bytes = await file.read()

        return await ask_document_question(
            student_id=student_id,
            filename=file.filename or "",
            file_bytes=file_bytes,
            question=question,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        await file.close()

@router.post("/image/analyse")
async def analyse_uploaded_image(
    student_id: int,
    question: str = "Explain this image in detail.",
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        image_bytes = await file.read()

        return await analyse_study_image(
            student_id=student_id,
            image_bytes=image_bytes,
            filename=file.filename or "",
            question=question,
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        await file.close()

@router.post("/conversations")
def create_agent_conversation(
    student_id: int,
    title: str = "New Conversation",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    return create_conversation(
        session=session,
        student_id=student_id,
        title=title,
    )

@router.post("/conversations/{conversation_id}/messages")
async def send_conversation_message(
    conversation_id: int,
    student_id: int,
    message: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        history = get_conversation_history(
            session,
            student_id,
            conversation_id,
        )

        conversation = session.get(
            AgentConversation,
            conversation_id,
        )

        save_conversation_message(
            session,
            student_id,
            conversation_id,
            "user",
            message,
        )

        result = await run_chat(
            session=session,
            student_id=student_id,
            message=message,
            conversation_history=history,
            conversation_summary=conversation.summary if conversation else None,
        )

        save_conversation_message(
            session,
            student_id,
            conversation_id,
            "assistant",
            result["response"],
        )

        message_count = session.exec(
            select(AgentMessage).where(
                AgentMessage.conversation_id == conversation_id,
                AgentMessage.student_id == student_id,
            )
        ).all()

        if len(message_count) % 20 == 0:
            await update_conversation_summary(
                session=session,
                student_id=student_id,
                conversation_id=conversation_id,
            )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

@router.get("/conversations")
def list_agent_conversations(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    conversations = session.exec(
        select(AgentConversation)
        .where(AgentConversation.student_id == student_id)
        .order_by(AgentConversation.updated_at.desc())
    ).all()

    return [
        {
            "id": item.id,
            "title": item.title,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
        for item in conversations
    ]

@router.get("/conversations/{conversation_id}/messages")
def get_agent_messages(
    conversation_id: int,
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return get_conversation_history(
            session=session,
            student_id=student_id,
            conversation_id=conversation_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.delete("/conversations/{conversation_id}")
def remove_agent_conversation(
    conversation_id: int,
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return delete_conversation(
            session=session,
            student_id=student_id,
            conversation_id=conversation_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.patch("/conversations/{conversation_id}")
def update_agent_conversation(
    conversation_id: int,
    student_id: int,
    new_title: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return rename_conversation(
            session=session,
            student_id=student_id,
            conversation_id=conversation_id,
            new_title=new_title,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.delete("/conversations/{conversation_id}/messages")
def clear_agent_messages(
    conversation_id: int,
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return clear_conversation_history(
            session=session,
            student_id=student_id,
            conversation_id=conversation_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

from fastapi.responses import Response


@router.get("/conversations/{conversation_id}/export")
def download_agent_conversation(
    conversation_id: int,
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        result = export_conversation(
            session=session,
            student_id=student_id,
            conversation_id=conversation_id,
        )

        return Response(
            content=result["content"],
            media_type="text/markdown",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{result["filename"]}"'
                )
            },
        )

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.get("/conversations/search")
def search_agent_conversations(
    student_id: int,
    query: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return search_conversations(
            session=session,
            student_id=student_id,
            query=query,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/conversations/search-messages")
def search_agent_messages(
    student_id: int,
    query: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return search_conversation_messages(
            session=session,
            student_id=student_id,
            query=query,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/conversations/recent")
def recent_agent_conversations(
    student_id: int,
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return get_recent_conversations(
            session=session,
            student_id=student_id,
            limit=limit,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/conversations/{conversation_id}/summarize")
async def summarize_agent_conversation(
    conversation_id: int,
    student_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    get_owned_student(student_id, current_user, session)

    try:
        return await update_conversation_summary(
            session=session,
            student_id=student_id,
            conversation_id=conversation_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))