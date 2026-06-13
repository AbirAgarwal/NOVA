from ollama import chat

SYSTEM_PROMPT = """
You are NOVA.

Keep responses short and direct.
Maximum 2 sentences unless explicitly asked for details.

You are Abir's personal AI operating companion.
"""


def get_ai_response(user_text):
    response = chat(
        model="qwen3:1.7b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )

    return response["message"]["content"]