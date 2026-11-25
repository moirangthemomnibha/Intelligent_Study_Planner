import os
import json
import logging
from typing import Callable, Any
from app.core.config import settings

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class AgentToolRegistry:
    """Registers functions that the AI agent can execute."""

    def clear(self):
        self.tools.clear()
        self.definitions.clear()

    def __init__(self):
        self.tools = {}
        self.definitions = []

    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        function: Callable
    ):
        self.tools[name] = function

        self.definitions.append({
            "type": "function",
            "name": name,
            "description": description,
            "parameters": parameters,
            "strict": False
        })

    async def execute(self, name: str, arguments: dict):
        function = self.tools.get(name)

        if function is None:
            raise ValueError(f"Unknown agent tool: {name}")

        result = function(**arguments)

        if hasattr(result, "__await__"):
            result = await result

        return result


class AgenticStudyAssistant:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )

        self.model = settings.ai_model
        self.registry = AgentToolRegistry()

        self.max_tool_rounds = 8

        self.instructions = """
You are the central Agentic AI Study Assistant.

Your responsibility is to help students manage their academic life.

You can:

1. Understand student requests.
2. Analyse academic information.
3. Plan study schedules.
4. Prioritise subjects and topics.
5. Manage study tasks.
6. Analyse student progress.
7. Help with academic questions.
8. Summarise study materials.
9. Generate revision strategies.
10. Recommend appropriate learning activities.

AGENT BEHAVIOUR:

- Understand the user's actual intention.
- Use available tools whenever real application data or actions are required.
- Do not invent student information.
- Never claim an operation succeeded unless the tool confirms it.
- Use multiple tools when necessary.
- Analyse tool results before deciding the next action.
- Respect the student's available study time and deadlines.
- Do not modify profile or application settings.
- Never delete student data without explicit confirmation.
- Do not expose another student's information.
- Explain completed actions clearly.

LANGUAGE:

- Understand English and Hindi.
- Respond in the language used by the student.
- Keep explanations clear and student-friendly.

You are an academic assistant, not merely a chatbot.
Your purpose is to understand, decide, execute and adapt.
"""

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: dict,
        function: Callable
    ):
        self.registry.register(
            name,
            description,
            parameters,
            function
        )

    async def run(
        self,
        message: str,
        conversation_history: list = None,
        student_context: dict = None
    ) -> dict:

        if not message.strip():
            raise ValueError("Message cannot be empty.")

        history = conversation_history or []

        context = student_context or {}

        input_messages = [
            {
                "role": "user",
                "content": (
                    f"Student context:\n"
                    f"{json.dumps(context, default=str)}\n\n"
                    f"Student request:\n{message}"
                )
            }
        ]

        for item in history[-10:]:
            if item.get("role") in ("user", "assistant"):
                input_messages.insert(
                    -1,
                    {
                        "role": item["role"],
                        "content": item["content"]
                    }
                )

        executed_actions = []

        for _ in range(self.max_tool_rounds):

            response = await self.client.responses.create(
                model=self.model,
                instructions=self.instructions,
                input=input_messages,
                tools=self.registry.definitions,
                tool_choice="auto",
                store=False
            )

            function_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not function_calls:
                return {
                    "success": True,
                    "response": response.output_text,
                    "actions": executed_actions
                }

            input_messages.extend(response.output)

            for call in function_calls:

                try:
                    arguments = json.loads(call.arguments)

                    result = await self.registry.execute(
                        call.name,
                        arguments
                    )

                    executed_actions.append({
                        "tool": call.name,
                        "status": "success"
                    })

                    output = {
                        "success": True,
                        "result": result
                    }

                except Exception as error:

                    logger.exception(
                        "Agent tool execution failed: %s",
                        call.name
                    )

                    output = {
                        "success": False,
                        "error": str(error)
                    }

                input_messages.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(
                        output,
                        default=str
                    )
                })

        return {
            "success": False,
            "response": (
                "The request requires more operations than "
                "the current execution limit allows."
            ),
            "actions": executed_actions
        }

def get_agent():
    return AgenticStudyAssistant()