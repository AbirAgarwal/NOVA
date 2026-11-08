from ollama import chat
from memory_manager import get_memory_context

# Faster default model — change via GUI model selector or here
AI_MODEL = "qwen3:1.8b"

SYSTEM_PROMPT = """
You are NOVA, Abir's personal AI operating companion.

Rules:
- Be concise and practical.
- Give direct answers.
- Use memory context when relevant.
- Help with coding, projects, hackathons, study plans, and productivity.
- Never mention being an AI language model.
- Act like an intelligent desktop assistant.
- Use bullet points when useful.
- Keep replies under 3 sentences unless detailed explanations are requested.
"""

conversation = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


def set_ai_model(model_name: str):
    global AI_MODEL
    AI_MODEL = model_name


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
        model=AI_MODEL,
        messages=conversation
    )

    reply = response["message"]["content"]

    conversation.append(
        {
            "role": "assistant",
            "content": reply
        }
    )
    # Keep only recent conversation
    if len(conversation) > 60:
        conversation[:] = [conversation[0]] + conversation[-59:]
    return reply


def stream_ai_response(user_text):

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

    stream = chat(
        model=AI_MODEL,
        messages=conversation,
        stream=True
    )

    full_reply = ""

    for chunk in stream:

        content = chunk["message"]["content"]

        full_reply += content

        yield content

    conversation.append(
        {
            "role": "assistant",
            "content": full_reply
        }
    )
    if len(conversation) > 60:
        conversation[:] = [conversation[0]] + conversation[-59:]
