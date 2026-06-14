from ai_brain import get_ai_response


def find_bugs(filename):

    try:

        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()[:8000]

        prompt = f"""
Analyze this Python code.

Tell me:
1. Bugs
2. Potential errors
3. Bad coding practices
4. Improvements

Code:

{code}
"""

        return get_ai_response(prompt)

    except Exception as e:
        return f"Error: {e}"