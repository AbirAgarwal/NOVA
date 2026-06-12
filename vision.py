from PIL import ImageGrab
from datetime import datetime
import os


def capture_screen():

    os.makedirs("screenshots", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    path = f"screenshots/{timestamp}.png"

    screenshot = ImageGrab.grab()
    screenshot.save(path)

    return path