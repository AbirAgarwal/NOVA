from ollama import chat
from memory_manager import get_memory_context

SYSTEM_PROMPT = """
You are NOVA.

Keep responses short and direct.
Maximum 2 sentences unless explicitly asked for details.

You are Abir's personal AI operating companion.
"""

conversation = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


def get_ai_response(user_text):

    memory_context = get_memory_context()

    conversation[0] = {
        "role": "system",
        "content": SYSTEM_PROMPT + "\n\n" + memory_context
    }

    conversation.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    response = chat(
        model="qwen3:1.7b",
        messages=conversation
    )

    reply = response["message"]["content"]

    conversation.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    return reply