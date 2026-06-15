import pytesseract

from PIL import Image


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def read_text_from_image(filename):

    try:

        image = Image.open(filename)

        text = pytesseract.image_to_string(image)

        text = text.strip()

        if not text:

            return "No text found in image."

        return text

    except Exception as e:

        return f"Error: {e}"