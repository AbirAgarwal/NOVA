import os
import webbrowser
import subprocess
import psutil

from urllib.parse import quote
from datetime import datetime

from vision import capture_screen


# ======================
# WEBSITE ACTIONS
# ======================

def open_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube"


def open_google():
    webbrowser.open("https://www.google.com")
    return "Opening Google"


def open_github():
    webbrowser.open("https://github.com")
    return "Opening GitHub"


def search_google(query):
    webbrowser.open(
        f"https://www.google.com/search?q={quote(query)}"
    )
    return f"Searching Google for {query}"


def search_youtube(query):
    webbrowser.open(
        f"https://www.youtube.com/results?search_query={quote(query)}"
    )
    return f"Searching YouTube for {query}"


# ======================
# APPLICATION ACTIONS
# ======================

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


def open_chrome():
    os.system("start chrome")
    return "Opening Chrome"


# ======================
# FOLDER ACTIONS
# ======================

def open_downloads():
    os.startfile(
        os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )
    )
    return "Opening Downloads"


def open_documents():
    os.startfile(
        os.path.join(
            os.path.expanduser("~"),
            "Documents"
        )
    )
    return "Opening Documents"


def open_desktop():
    os.startfile(
        os.path.join(
            os.path.expanduser("~"),
            "Desktop"
        )
    )
    return "Opening Desktop"


def open_file_explorer():
    os.system("explorer")
    return "Opening File Explorer"


# ======================
# SCREENSHOT
# ======================

def take_screenshot():

    path = capture_screen()

    return f"Screenshot saved as {path}"


# ======================
# FILE CREATION
# ======================

def create_text_file(filename):

    if not filename.endswith(".txt"):
        filename += ".txt"

    with open(filename, "w", encoding="utf-8"):
        pass

    return f"Created {filename}"


def create_python_file(filename):

    if not filename.endswith(".py"):
        filename += ".py"

    with open(filename, "w", encoding="utf-8"):
        pass

    return f"Created {filename}"


def create_folder(foldername):

    os.makedirs(foldername, exist_ok=True)

    return f"Created folder {foldername}"


# ======================
# PROJECT GENERATOR
# ======================

def create_python_project(project_name):

    folder = project_name.replace(" ", "_")

    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/main.py", "w", encoding="utf-8") as f:
        f.write('print("Hello World")')

    with open(f"{folder}/README.md", "w", encoding="utf-8") as f:
        f.write(f"# {project_name}\n")

    with open(f"{folder}/requirements.txt", "w", encoding="utf-8"):
        pass

    return f"Created Python project {project_name}"


# ======================
# SYSTEM INFO
# ======================

def get_time():
    return f"The time is {datetime.now().strftime('%I:%M %p')}"


def get_date():
    return f"Today is {datetime.now().strftime('%B %d, %Y')}"


def get_battery_status():

    battery = psutil.sensors_battery()

    if battery:

        percent = battery.percent

        if battery.power_plugged:
            return f"Battery is at {percent} percent and charging."

        return f"Battery is at {percent} percent."

    return "I could not detect the battery."


def get_system_info():

    cpu = psutil.cpu_percent(interval=1)

    ram = psutil.virtual_memory().percent

    return (
        f"CPU usage is {cpu} percent. "
        f"Memory usage is {ram} percent."
    )