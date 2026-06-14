from ai_brain import get_ai_response


def explain_file(filename):

    try:

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()[:8000]

        prompt = f"""
Explain this Python code in simple language.

Tell me:
1. What the file does
2. Main functions
3. Important logic

Code:

{content}
"""

        return get_ai_response(prompt)

    except Exception as e:
        return f"Error: {e}"