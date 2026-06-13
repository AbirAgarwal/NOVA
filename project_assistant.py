from ai_brain import get_ai_response


def generate_code(prompt):

    full_prompt = f"""
Write only Python code.

Task:
{prompt}
"""

    return get_ai_response(full_prompt)