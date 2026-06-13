from ai_brain import get_ai_response


def improve_file(filename):

    try:

        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()

        prompt = f"""
Improve this Python code.

Requirements:
- Better formatting
- Better variable names
- Add useful comments
- Keep functionality unchanged

Return only Python code.

Code:
{code}
"""

        improved_code = get_ai_response(prompt)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(improved_code)

        return f"Improved {filename}"

    except Exception as e:
        return f"Error: {e}"