from ai_brain import get_ai_response


def fix_file(filename):

    try:

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            code = f.read()[:8000]

        prompt = f"""
Fix this Python code.

Return ONLY the corrected code.

Code:

{code}
"""

        fixed_code = get_ai_response(prompt)

        backup = filename + ".bak"

        with open(
            backup,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(code)

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(fixed_code)

        return f"Fixed {filename}"

    except Exception as e:

        return f"Error: {e}"