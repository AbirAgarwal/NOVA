from ai_brain import get_ai_response


def generate_readme(project_name):

    prompt = f"""
Create a professional GitHub README.

Project Name:
{project_name}

Include:
- Project title
- Description
- Features
- Installation
- Usage

Return only markdown.
"""

    return get_ai_response(prompt)