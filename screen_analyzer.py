from ocr_reader import read_text_from_image
from ai_brain import get_ai_response


def analyze_screen(image_path):

    text = read_text_from_image(image_path)

    if len(text.strip()) < 10:
        return "I could not understand the screen."

    prompt = f"""
Analyze this screen text and explain what the user is looking at.

{text}
"""

    return get_ai_response(prompt)