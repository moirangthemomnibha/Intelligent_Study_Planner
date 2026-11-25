"""Agentic AI orchestration for Intelligent Study Planner."""

from app.modules.agent.scheduling_agent import (
    detect_missed_sessions,
    reschedule_missed_sessions,
)

from datetime import date, datetime, timezone
from sqlmodel import Session, select

from app.modules.students.models import Student
from app.modules.subjects.models import Subject
from app.modules.topics.models import Topic
from app.modules.sessions.models import StudySession

from app.modules.ai.service import recommend_next_action
from app.modules.planning.service import generate_plan
from app.modules.agent.engine import get_agent
from app.modules.agent.conversation_models import AgentConversation, AgentMessage


def get_student_summary(session: Session, student_id: int) -> dict:

    student = session.get(Student, student_id)

    if student is None:
        raise ValueError("Student not found.")

    results = session.exec(
        select(Topic, Subject)
        .join(Subject, Topic.subject_id == Subject.id)
        .where(Subject.student_id == student_id)
    ).all()

    topics = []

    for topic, subject in results:

        try:
            days_to_exam = (
                date.fromisoformat(subject.exam_date) - date.today()
            ).days
        except (ValueError, TypeError):
            days_to_exam = 30

        topics.append({
            "id": topic.id,
            "topic_id": topic.id,
            "name": topic.name,
            "subject_id": subject.id,
            "subject_name": subject.name,
            "estimated_minutes": topic.estimated_minutes,
            "difficulty": topic.difficulty,
            "completion_percent": topic.completion_percent,
            "confidence": topic.confidence,
            "priority": topic.priority,
            "exam_weight": subject.exam_weight,
            "days_to_exam": days_to_exam,
        })

    sessions = session.exec(
        select(StudySession)
        .where(StudySession.student_id == student_id)
    ).all()

    return {
        "student_id": student_id,
        "topics": topics,
        "sessions": [
            {
                "id": item.id,
                "topic_id": item.topic_id,
                "date": item.planned_date,
                "status": item.status,
                "planned_minutes": item.planned_minutes,
                "actual_minutes": item.actual_minutes,
            }
            for item in sessions
        ],
    }


def get_deadline_risks(topics: list) -> list:

    risks = []

    for topic in topics:

        if (
            topic["completion_percent"] < 100
            and topic["days_to_exam"] <= 7
        ):
            risks.append({
                "topic": topic["name"],
                "days_remaining": topic["days_to_exam"],
                "completion": topic["completion_percent"],
                "risk": "High",
            })

    return risks


async def run_agent(
    session: Session,
    student_id: int,
    intent: str,
    available_minutes: int,
    horizon_days: int,
    approval_mode: str,
) -> dict:

    summary = get_student_summary(session, student_id)

    if not summary["topics"]:
        return {
            "summary": "Please add subjects and topics first.",
            "actions": [],
            "requires_confirmation": False,
        }

    agent = get_agent()
    agent.registry.clear()

    # TOOL 1: Retrieve academic information.
    def observe_student():
        return get_student_summary(session, student_id)

    # TOOL 2: Analyse examination risks.
    def analyse_deadlines():
        return get_deadline_risks(summary["topics"])

    # TOOL 3: Generate an intelligent study schedule.
    def generate_study_schedule(
        daily_minutes: int,
        planning_days: int,
    ):

        if not 1 <= daily_minutes <= 1440:
            raise ValueError("Invalid daily study time.")

        if not 1 <= planning_days <= 30:
            raise ValueError("Planning period must be 1-30 days.")

        recommendation = recommend_next_action(summary)

        plan = generate_plan(
            topics=summary["topics"],
            available_minutes=daily_minutes,
            days=planning_days,
            start_date=date.today(),
        )

        return {
            "start_date": date.today().isoformat(),
            "horizon_days": planning_days,
            "available_minutes_per_day": daily_minutes,
            "sessions": plan,
            "recommendation": recommendation,
        }

    # Register tools.
    agent.register_tool(
        name="get_student_academic_data",
        description="Retrieve the student's subjects, topics, progress and study sessions.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        function=observe_student,
    )

    agent.register_tool(
        name="analyse_exam_deadlines",
        description="Analyse unfinished topics and identify approaching examination deadlines.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        function=analyse_deadlines,
    )

    agent.register_tool(
        name="generate_study_schedule",
        description="Generate a personalised study schedule using available time and planning period.",
        parameters={
            "type": "object",
            "properties": {
                "daily_minutes": {
                    "type": "integer",
                    "description": "Available study minutes per day.",
                },
                "planning_days": {
                    "type": "integer",
                    "description": "Number of days to plan.",
                },
            },
            "required": [
                "daily_minutes",
                "planning_days",
            ],
            "additionalProperties": False,
        },
        function=generate_study_schedule,
    )

    # Execute the agent.
    result = await agent.run(
    message=intent,
    student_context={
        "conversation_summary": conversation_summary,
        "student_id": student_id,
        "available_minutes": available_minutes,
        "horizon_days": horizon_days,
        "approval_mode": approval_mode,
        "academic_data": summary,
    },
)

    return {
        "summary": result["response"],
        "actions": result["actions"],
        "requires_confirmation": (
            approval_mode == "ask_before_changes"
        ),
    }
async def run_chat(
    session: Session,
    student_id: int,
    message: str,
    conversation_history: list,
    conversation_summary: str | None = None,
) -> dict:

    summary = get_student_summary(session, student_id)

    agent = get_agent()
    agent.registry.clear()

    def get_academic_data():
        return get_student_summary(session, student_id)

    def analyse_deadlines():
        return get_deadline_risks(summary["topics"])

    def generate_study_schedule(
        daily_minutes: int,
        planning_days: int,
    ):
        if not 1 <= daily_minutes <= 1440:
            raise ValueError("Invalid daily study time.")

        if not 1 <= planning_days <= 30:
            raise ValueError("Planning period must be 1-30 days.")

        plan = generate_plan(
            topics=summary["topics"],
            available_minutes=daily_minutes,
            days=planning_days,
            start_date=date.today(),
        )

        return {
            "sessions": plan,
            "planning_days": planning_days,
            "daily_minutes": daily_minutes,
        }

    agent.register_tool(
        name="get_student_academic_data",
        description="Retrieve the student's academic data and study progress.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        function=get_academic_data,
    )

    agent.register_tool(
        name="analyse_exam_deadlines",
        description="Identify unfinished topics with approaching examination deadlines.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        function=analyse_deadlines,
    )

    agent.register_tool(
        name="generate_study_schedule",
        description="Generate a personalised study schedule.",
        parameters={
            "type": "object",
            "properties": {
                "daily_minutes": {
                    "type": "integer",
                },
                "planning_days": {
                    "type": "integer",
                },
            },
            "required": [
                "daily_minutes",
                "planning_days",
            ],
            "additionalProperties": False,
        },
        function=generate_study_schedule,
    )

    return await agent.run(
        message=message,
        conversation_history=conversation_history[-20:],
        student_context={
            "student_id": student_id,
            "academic_data": summary,
            "conversation_summary": conversation_summary,
        },
    )

from app.modules.agent.document_service import extract_document_text


async def summarize_document(
    filename: str,
    file_bytes: bytes,
    summary_type: str = "detailed",
) -> dict:

    document = extract_document_text(
        filename,
        file_bytes,
    )

    if document["characters"] > 50000:
        raise ValueError(
            "Document is too large for processing. Maximum extracted text is 50,000 characters."
        )

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Analyse the following study material.

Create a {summary_type} summary.

Include:
1. Main concepts.
2. Important definitions.
3. Key points.
4. Important formulas, if present.
5. Examination-relevant information.

Preserve the meaning of the original material.

DOCUMENT:
{document["text"]}
""",
        student_context={
            "filename": filename,
            "task": "document_summarisation",
        },
    )

    return {
        "success": result["success"],
        "filename": filename,
        "summary": result["response"],
    }

def recover_missed_study_sessions(
    session: Session,
    student_id: int,
    available_minutes_per_day: int = 180,
) -> dict:

    missed = detect_missed_sessions(
        session=session,
        student_id=student_id,
    )

    rescheduled = reschedule_missed_sessions(
        session=session,
        student_id=student_id,
        available_minutes_per_day=available_minutes_per_day,
    )

    return {
        "detected_missed_sessions": len(missed),
        "rescheduled_sessions": rescheduled,
        "details": missed,
    }

async def generate_quiz(
    student_id: int,
    topic: str,
    question_count: int = 10,
    difficulty: str = "mixed",
) -> dict:

    if not 1 <= question_count <= 50:
        raise ValueError("Question count must be between 1 and 50.")

    if difficulty not in {"easy", "medium", "hard", "mixed"}:
        raise ValueError("Invalid quiz difficulty.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Create a quiz for the student.

Topic: {topic}
Number of questions: {question_count}
Difficulty: {difficulty}

Requirements:
- Generate multiple-choice questions.
- Give four options per question.
- Include the correct answer.
- Explain why the answer is correct.
- Cover different aspects of the topic.
- Number every question clearly.
- Return the quiz in a well-organised format.
""",
        student_context={
            "student_id": student_id,
            "task": "quiz_generation",
        },
    )

    return {
        "success": result["success"],
        "topic": topic,
        "quiz": result["response"],
    }

async def generate_flashcards(
    student_id: int,
    topic: str,
    card_count: int = 10,
) -> dict:

    if not 1 <= card_count <= 50:
        raise ValueError("Card count must be between 1 and 50.")

    if not topic.strip():
        raise ValueError("Topic cannot be empty.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Create {card_count} study flashcards about: {topic}

Each flashcard must contain:
1. A clear question on the front.
2. A concise, accurate answer on the back.
3. Important definitions, concepts, or formulas where relevant.

Number each flashcard.
""",
        student_context={
            "student_id": student_id,
            "task": "flashcard_generation",
        },
    )

    return {
        "success": result["success"],
        "topic": topic,
        "flashcards": result["response"],
    }

async def evaluate_student_answer(
    student_id: int,
    question: str,
    expected_answer: str,
    student_answer: str,
) -> dict:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not expected_answer.strip():
        raise ValueError("Expected answer cannot be empty.")

    if not student_answer.strip():
        raise ValueError("Student answer cannot be empty.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Evaluate the student's answer.

QUESTION:
{question}

EXPECTED ANSWER:
{expected_answer}

STUDENT ANSWER:
{student_answer}

Provide:
1. Marks or score out of 10.
2. Correct points.
3. Missing or incorrect points.
4. Explanation of mistakes.
5. An improved model answer.
6. Suggestions for improvement.

Be fair. Award partial marks for correct understanding.
""",
        student_context={
            "student_id": student_id,
            "task": "answer_evaluation",
        },
    )

    return {
        "success": result["success"],
        "evaluation": result["response"],
    }

async def explain_concept(
    student_id: int,
    concept: str,
    level: str = "beginner",
) -> dict:

    if not concept.strip():
        raise ValueError("Concept cannot be empty.")

    if level not in {"beginner", "intermediate", "advanced"}:
        raise ValueError("Invalid explanation level.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Explain this academic concept: {concept}

Student level: {level}

Include:
1. Simple definition.
2. Detailed explanation.
3. Step-by-step breakdown.
4. Practical example.
5. Important points to remember.
6. Three questions to check understanding.

Use clear student-friendly language.
""",
        student_context={
            "student_id": student_id,
            "task": "concept_explanation",
        },
    )

    return {
        "success": result["success"],
        "concept": concept,
        "explanation": result["response"],
    }

async def translate_text(
    student_id: int,
    text: str,
    target_language: str,
) -> dict:

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    if not target_language.strip():
        raise ValueError("Target language cannot be empty.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Translate the following text into {target_language}.

Preserve:
- Original meaning.
- Technical and academic terminology.
- Formulas and code.
- Formatting and structure.

TEXT:
{text}
""",
        student_context={
            "student_id": student_id,
            "task": "translation",
        },
    )

    return {
        "success": result["success"],
        "target_language": target_language,
        "translation": result["response"],
    }

async def solve_academic_problem(
    student_id: int,
    problem: str,
    subject: str = "general",
) -> dict:

    if not problem.strip():
        raise ValueError("Problem cannot be empty.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Solve the following academic problem.

Subject: {subject}

Problem:
{problem}

Requirements:
1. Identify what is given.
2. Identify what needs to be found.
3. Explain the relevant concept or formula.
4. Solve step by step.
5. Show calculations clearly.
6. Provide the final answer.
7. Verify the result where possible.

For programming problems, provide code and explain its logic.
Do not invent missing information.
""",
        student_context={
            "student_id": student_id,
            "task": "academic_problem_solving",
        },
    )

    return {
        "success": result["success"],
        "subject": subject,
        "solution": result["response"],
    }

async def generate_revision_notes(
    student_id: int,
    topic: str,
    note_type: str = "exam-oriented",
) -> dict:

    if not topic.strip():
        raise ValueError("Topic cannot be empty.")

    if note_type not in {"brief", "detailed", "exam-oriented"}:
        raise ValueError("Invalid note type.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Create revision notes for: {topic}

Note type: {note_type}

Include relevant:
1. Key concepts.
2. Important definitions.
3. Formulas and explanations.
4. Examples.
5. Important examination points.
6. Quick revision summary.

Use clear headings and structured notes.
Do not invent facts or formulas.
""",
        student_context={
            "student_id": student_id,
            "task": "revision_notes",
        },
    )

    return {
        "success": result["success"],
        "topic": topic,
        "notes": result["response"],
    }

async def analyse_learning_progress(
    session: Session,
    student_id: int,
) -> dict:

    summary = get_student_summary(session, student_id)

    if not summary["topics"]:
        raise ValueError("No academic topics found.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Analyse this student's academic progress.

ACADEMIC DATA:
{summary}

Provide:
1. Overall learning progress.
2. Strong and weak topics.
3. Topics requiring immediate attention.
4. Study consistency based on recorded sessions.
5. Recommended improvements.
6. A practical action plan for the next seven days.

Use only the supplied academic data.
Do not invent statistics.
""",
        student_context={
            "student_id": student_id,
            "task": "learning_progress_analysis",
        },
    )

    return {
        "success": result["success"],
        "analysis": result["response"],
    }

async def generate_exam_questions(
    student_id: int,
    topic: str,
    question_count: int = 10,
    question_type: str = "mixed",
) -> dict:

    if not topic.strip():
        raise ValueError("Topic cannot be empty.")

    if not 1 <= question_count <= 50:
        raise ValueError("Question count must be between 1 and 50.")

    if question_type not in {"mcq", "short", "long", "mixed"}:
        raise ValueError("Invalid question type.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Generate {question_count} probable examination questions.

Topic: {topic}
Question type: {question_type}

Include:
1. Questions arranged by difficulty.
2. Marks for each question.
3. Important concepts tested.
4. Model answers.
5. A final list of high-priority revision areas.

Do not claim these questions will appear in an actual examination.
""",
        student_context={
            "student_id": student_id,
            "task": "exam_question_generation",
        },
    )

    return {
        "success": result["success"],
        "topic": topic,
        "questions": result["response"],
    }

async def generate_learning_roadmap(
    student_id: int,
    subject: str,
    goal: str,
    duration_days: int = 30,
) -> dict:

    if not subject.strip() or not goal.strip():
        raise ValueError("Subject and goal are required.")

    if not 1 <= duration_days <= 180:
        raise ValueError("Duration must be between 1 and 180 days.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Create a personalised learning roadmap.

Subject: {subject}
Learning goal: {goal}
Duration: {duration_days} days

Include:
1. Learning phases.
2. Topics to cover in each phase.
3. Recommended daily activities.
4. Practice exercises.
5. Revision checkpoints.
6. Progress milestones.
7. Final assessment.

Make the roadmap realistic and progressive.
""",
        student_context={
            "student_id": student_id,
            "task": "learning_roadmap",
        },
    )

    return {
        "success": result["success"],
        "subject": subject,
        "roadmap": result["response"],
    }

async def transcribe_voice_command(
    audio_bytes: bytes,
    filename: str,
) -> dict:

    if not audio_bytes:
        raise ValueError("Audio file is empty.")

    allowed_formats = {
        ".mp3", ".mp4", ".mpeg", ".mpga",
        ".m4a", ".wav", ".webm",
    }

    from pathlib import Path

    extension = Path(filename).suffix.lower()

    if extension not in allowed_formats:
        raise ValueError("Unsupported audio format.")

    agent = get_agent()

    transcription = await agent.client.audio.transcriptions.create(
        model="whisper-1",
        file=(filename, audio_bytes),
    )

    return {
        "success": True,
        "transcription": transcription.text,
    }

async def process_voice_command(
    session: Session,
    student_id: int,
    audio_bytes: bytes,
    filename: str,
) -> dict:

    transcription = await transcribe_voice_command(
        audio_bytes=audio_bytes,
        filename=filename,
    )

    text = transcription["transcription"].strip()

    if not text:
        raise ValueError("No speech detected.")

    response = await run_chat(
        session=session,
        student_id=student_id,
        message=text,
        conversation_history=[],
    )

    return {
        "success": response["success"],
        "transcription": text,
        "response": response["response"],
        "actions": response.get("actions", []),
    }

async def generate_voice_response(
    text: str,
) -> bytes:

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    agent = get_agent()

    response = await agent.client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    return response.content

async def ask_document_question(
    student_id: int,
    filename: str,
    file_bytes: bytes,
    question: str,
) -> dict:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    document = extract_document_text(filename, file_bytes)

    if document["characters"] > 50000:
        raise ValueError("Document exceeds the 50,000-character processing limit.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Answer the student's question using the uploaded document.

DOCUMENT:
{document["text"]}

STUDENT QUESTION:
{question}

Requirements:
- Base your answer on the document.
- Explain clearly.
- Include relevant definitions and examples.
- If the document does not contain the answer, say so.
- Do not invent information.
""",
        student_context={
            "student_id": student_id,
            "filename": filename,
            "task": "document_question_answering",
        },
    )

    return {
        "success": result["success"],
        "filename": filename,
        "answer": result["response"],
    }

import base64


async def analyse_study_image(
    student_id: int,
    image_bytes: bytes,
    filename: str,
    question: str = "Explain this image in detail.",
) -> dict:

    if not image_bytes:
        raise ValueError("Image is empty.")

    if len(image_bytes) > 10 * 1024 * 1024:
        raise ValueError("Image size cannot exceed 10 MB.")

    import mimetypes

    mime_type, _ = mimetypes.guess_type(filename)

    if mime_type not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise ValueError("Unsupported image format.")

    image_data = base64.b64encode(image_bytes).decode("utf-8")

    agent = get_agent()

    response = await agent.client.responses.create(
        model=agent.model,
        instructions=(
            "You are an academic image-analysis assistant. "
            "Explain diagrams, handwritten notes, equations, "
            "charts and educational images accurately. "
            "Do not invent unreadable content."
        ),
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": question},
                {
                    "type": "input_image",
                    "image_url": f"data:{mime_type};base64,{image_data}",
                },
            ],
        }],
        store=False,
    )

    return {
        "success": True,
        "analysis": response.output_text,
    }

def create_conversation(
    session: Session,
    student_id: int,
    title: str = "New Conversation",
) -> dict:

    conversation = AgentConversation(
        student_id=student_id,
        title=title,
    )

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return {
        "id": conversation.id,
        "student_id": conversation.student_id,
        "title": conversation.title,
    }

def save_conversation_message(
    session: Session,
    student_id: int,
    conversation_id: int,
    role: str,
    content: str,
) -> dict:

    if role not in {"user", "assistant"}:
        raise ValueError("Invalid message role.")

    if not content.strip():
        raise ValueError("Message cannot be empty.")

    if len(content) > 20000:
        raise ValueError("Message exceeds the 20,000-character limit.")

    conversation = session.get(
        AgentConversation,
        conversation_id,
    )

    if conversation is None or conversation.student_id != student_id:
        raise ValueError("Conversation not found.")

    message = AgentMessage(
        conversation_id=conversation_id,
        student_id=student_id,
        role=role,
        content=content,
    )

    conversation.updated_at = datetime.now(timezone.utc)

    if role == "user" and conversation.title == "New Conversation":
        conversation.title = content.strip()[:50]

    session.add(message)
    session.add(conversation)
    session.commit()
    session.refresh(message)

    return {
        "id": message.id,
        "conversation_id": conversation_id,
        "role": message.role,
        "content": message.content,
    }

def get_conversation_history(
    session: Session,
    student_id: int,
    conversation_id: int,
) -> list:

    conversation = session.get(
        AgentConversation,
        conversation_id,
    )

    if conversation is None or conversation.student_id != student_id:
        raise ValueError("Conversation not found.")

    messages = session.exec(
        select(AgentMessage)
        .where(
            AgentMessage.conversation_id == conversation_id,
            AgentMessage.student_id == student_id,
        )
        .order_by(AgentMessage.created_at.desc())
        .limit(20)
    ).all()

    messages.reverse()

    return [
        {
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]

def delete_conversation(
    session: Session,
    student_id: int,
    conversation_id: int,
) -> dict:

    conversation = session.get(
        AgentConversation,
        conversation_id,
    )

    if conversation is None or conversation.student_id != student_id:
        raise ValueError("Conversation not found.")

    messages = session.exec(
        select(AgentMessage).where(
            AgentMessage.conversation_id == conversation_id,
            AgentMessage.student_id == student_id,
        )
    ).all()

    for message in messages:
        session.delete(message)

    session.delete(conversation)
    session.commit()

    return {
        "success": True,
        "message": "Conversation deleted successfully.",
    }

def rename_conversation(
    session: Session,
    student_id: int,
    conversation_id: int,
    new_title: str,
) -> dict:

    if not new_title.strip():
        raise ValueError("Conversation title cannot be empty.")

    conversation = session.get(
        AgentConversation,
        conversation_id,
    )

    if conversation is None or conversation.student_id != student_id:
        raise ValueError("Conversation not found.")

    conversation.title = new_title.strip()[:100]
    conversation.updated_at = datetime.now(timezone.utc)

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return {
        "success": True,
        "id": conversation.id,
        "title": conversation.title,
    }

def clear_conversation_history(
    session: Session,
    student_id: int,
    conversation_id: int,
) -> dict:

    conversation = session.get(
        AgentConversation,
        conversation_id,
    )

    if conversation is None or conversation.student_id != student_id:
        raise ValueError("Conversation not found.")

    messages = session.exec(
        select(AgentMessage).where(
            AgentMessage.conversation_id == conversation_id,
            AgentMessage.student_id == student_id,
        )
    ).all()

    for message in messages:
        session.delete(message)

    conversation.updated_at = datetime.now(timezone.utc)

    session.add(conversation)
    session.commit()

    return {
        "success": True,
        "message": "Conversation history cleared.",
    }

def export_conversation(
    session: Session,
    student_id: int,
    conversation_id: int,
) -> dict:

    conversation = session.get(
        AgentConversation,
        conversation_id,
    )

    if conversation is None or conversation.student_id != student_id:
        raise ValueError("Conversation not found.")

    messages = get_conversation_history(
        session,
        student_id,
        conversation_id,
    )

    content = f"# {conversation.title}\n\n"

    for message in messages:
        role = message["role"].capitalize()
        content += f"## {role}\n\n{message['content']}\n\n"

    return {
        "success": True,
        "filename": f"conversation_{conversation_id}.md",
        "content": content,
    }

def search_conversations(
    session: Session,
    student_id: int,
    query: str,
) -> list:

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    conversations = session.exec(
        select(AgentConversation)
        .where(
            AgentConversation.student_id == student_id,
            AgentConversation.title.contains(query.strip()),
        )
        .order_by(AgentConversation.updated_at.desc())
    ).all()

    return [
        {
            "id": item.id,
            "title": item.title,
            "updated_at": item.updated_at,
        }
        for item in conversations
    ]

def search_conversation_messages(
    session: Session,
    student_id: int,
    query: str,
) -> list:

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    messages = session.exec(
        select(AgentMessage)
        .where(
            AgentMessage.student_id == student_id,
            AgentMessage.content.contains(query.strip()),
        )
        .order_by(AgentMessage.created_at.desc())
    ).all()

    return [
        {
            "id": item.id,
            "conversation_id": item.conversation_id,
            "role": item.role,
            "content": item.content,
            "created_at": item.created_at,
        }
        for item in messages
    ]

def get_recent_conversations(
    session: Session,
    student_id: int,
    limit: int = 20,
) -> list:

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    conversations = session.exec(
        select(AgentConversation)
        .where(AgentConversation.student_id == student_id)
        .order_by(AgentConversation.updated_at.desc())
        .limit(limit)
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

async def update_conversation_summary(
    session: Session,
    student_id: int,
    conversation_id: int,
) -> dict:

    conversation = session.get(
        AgentConversation,
        conversation_id,
    )

    if conversation is None or conversation.student_id != student_id:
        raise ValueError("Conversation not found.")

    messages = get_conversation_history(
        session,
        student_id,
        conversation_id,
    )

    if not messages:
        raise ValueError("No messages to summarise.")

    agent = get_agent()
    agent.registry.clear()

    result = await agent.run(
        message=f"""
Create a concise summary of this conversation.

Preserve:
- Student's goals and preferences.
- Important academic questions.
- Concepts already explained.
- Decisions and unfinished tasks.
- Relevant context for future replies.

CONVERSATION:
{messages}
""",
        student_context={
            "student_id": student_id,
            "task": "conversation_memory",
        },
    )

    conversation.summary = result["response"]
    conversation.updated_at = datetime.now(timezone.utc)

    session.add(conversation)
    session.commit()

    return {
        "success": result["success"],
        "summary": conversation.summary,
    }