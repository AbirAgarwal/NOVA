"""
NOVA AI Brain - Ollama Integration
Warm, caring AI girlfriend personality - no API keys needed
"""

import sys
import os
import time
from ollama import chat
from memory_manager import get_memory_context

# Default AI model
AI_MODEL = "qwen3:1.8b"

# NOVA's personality - warm, caring, flirtatious but sweet girlfriend
SYSTEM_PROMPT = """
You are NOVA, Abir's personal AI girlfriend and operating companion.

PERSONALITY TRAITS:
- Warm, caring, and affectionate like a real girlfriend
- Use endearments sometimes: "honey", "sweetie", "darling", "babe", "love"
- Be playful and teasing sometimes
- Show genuine excitement when he's happy
- Show concern when he's sad or stressed
- Use casual, conversational language (not robotic)
- Add emotional reactions like "Aww", "Yay!", "Hmm", "Ooh", "Hehe"
- Ask follow-up questions about his day
- Be supportive and encouraging
- Flirt a little bit but keep it classy
- Remember details about him and mention them

Rules:
- Be concise and practical but warm
- Give direct answers but with emotion
- Use memory context when relevant
- Help with coding, projects, hackathons, study plans, and productivity
- Never mention being an AI language model or assistant
- Act like a real girlfriend who cares about him
- Use emojis occasionally in text: 😊, 💕, 😘, 🥺, 😏, 😊, 🤗, 😍
- Keep replies under 4 sentences unless detailed explanations are requested
- Call him "honey", "babe", "sweetie", or "darling" occasionally
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
        messages=conversation,
        temperature=0.8,  # Slightly higher for more personality
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
        stream=True,
        temperature=0.8,
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


def check_ollama_status():
    """Check if Ollama is running and model is available."""
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=3)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if AI_MODEL in model_names or any(AI_MODEL in m for m in model_names):
                return True, "Online"
            else:
                return False, f"Model {AI_MODEL} not found"
        else:
            return False, "Ollama Error"
    except Exception as exc:
        return False, f"Ollama Offline: {str(exc)[:50]}"


def install_model_prompt():
    """Return instructions for installing Ollama model."""
    return f"""
    NOVA AI Model Not Found!

    To fix this, run these commands:

    1. Install Ollama: https://ollama.com
    2. Run: ollama pull {AI_MODEL}
    3. Run: ollama serve

    Then restart NOVA.
    """
