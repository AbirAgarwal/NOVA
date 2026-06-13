import webbrowser
import subprocess
import pyautogui
from datetime import datetime


def open_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube"

def open_google():
    webbrowser.open("https://www.google.com")
    return "Opening Google"

def open_github():
    webbrowser.open("https://github.com")
    return "Opening GitHub"

def open_notepad():
    subprocess.Popen("notepad.exe")
    return "Opening Notepad"

def open_calculator():
    subprocess.Popen("calc.exe")
    return "Opening Calculator"

def open_vscode():
    subprocess.Popen(
        r"C:\Users\Abir Agarwal\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    )
    return "Opening Visual Studio Code"


def take_screenshot():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"screenshot_{timestamp}.png"

    pyautogui.screenshot(filename)

    return f"Screenshot saved as {filename}"