from groq import Groq
from memory_manager import get_memory_context
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AI_MODEL = "llama3-8b-8192"  # Fast Groq model - change to llama3-70b-8192 for better quality

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

client = Groq(api_key=GROQ_API_KEY)


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

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=conversation,
        temperature=0.7,
        max_tokens=500
    )

    reply = response.choices[0].message.content

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

    stream = client.chat.completions.create(
        model=AI_MODEL,
        messages=conversation,
        stream=True,
        temperature=0.7,
        max_tokens=500
    )

    full_reply = ""

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
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
