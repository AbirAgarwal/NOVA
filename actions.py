import os
import webbrowser
import subprocess
import psutil
from urllib.parse import quote
from datetime import datetime
from vision import capture_screen
from memory_manager import (get_dashboard, list_tasks)

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

def open_website(url):

    url = url.strip()

    if not url.startswith(
        ("http://", "https://")
    ):
        url = "https://" + url

    webbrowser.open(url)

    return f"Opening {url}"

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

    os.startfile(folder)

    return f"Created and opened Python project {project_name}"


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

def read_chat_history():

    try:
        with open("chat_history.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        recent = "".join(lines[-20:])

        return recent

    except:
        return "No chat history found."

def generate_python_program(filename, prompt):

    from project_assistant import generate_code

    code = generate_code(prompt)

    if not filename.endswith(".py"):
        filename += ".py"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    return f"Generated {filename}"

def improve_python_file(filename):

    from code_editor import improve_file

    return improve_file(filename) 

# ======================
# WORKSPACE MODES
# ======================

def start_coding():

    open_vscode()
    open_github()
    open_chrome()

    return "Coding workspace ready."


def hackathon_mode():

    open_vscode()
    open_github()
    open_youtube()

    return "Hackathon mode activated."


def study_mode():

    open_google()
    open_youtube()

    return "Study mode activated."  

# ======================
# PROJECT MANAGER
# ======================

def list_projects():

    projects = []

    for item in os.listdir():

        if os.path.isdir(item):

            has_main = os.path.exists(
                os.path.join(item, "main.py")
            )

            has_readme = os.path.exists(
                os.path.join(item, "README.md")
            )

            if has_main or has_readme:
                projects.append(item)

    if not projects:
        return "No projects found."

    return "Projects: " + ", ".join(projects)


def open_project(project_name):

    target = project_name.lower().replace(" ", "_")

    for item in os.listdir():

        if os.path.isdir(item):

            if item.lower() == target:

                os.startfile(item)

                return f"Opening project {item}"

    return "Project not found."

def explain_python_file(filename):

    from file_explainer import explain_file

    return explain_file(filename)

def generate_project_readme(project_name):

    from readme_generator import generate_readme

    content = generate_readme(project_name)

    filename = f"{project_name.replace(' ', '_')}_README.md"

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)

    return f"Generated {filename}"

def find_bugs_in_file(filename):

    from bug_finder import find_bugs

    return find_bugs(filename)

def fix_python_file(filename):

    from code_fixer import fix_file

    return fix_file(filename)

def start_project(project_name):

    create_python_project(project_name)

    try:
        open_vscode()
    except:
        pass

    
    return f"Project workspace ready for {project_name}"

def work_on_project(project_name):

    project_folder = (
        project_name
        .lower()
        .replace(" ", "_")
    )

    # Open VS Code

    try:
        open_vscode()
    except:
        pass

    # Open project folder

    try:
        open_project(project_folder)
    except:
        pass

    # Open github

    try:
        open_github()
    except:
        pass

    # Open README

    readme = (
        f"{project_folder}/README.md"
    )

    if os.path.exists(readme):

        try:
            os.startfile(readme)
        except:
            pass

    # Open roadmap

    roadmap = (
        f"{project_folder}/roadmap.md"
    )

    if os.path.exists(roadmap):

        try:
            os.startfile(roadmap)
        except:
            pass

    return (
        f"Project workspace ready "
        f"for {project_name}"
    )


def hackathon_setup():

    open_vscode()
    open_github()

    webbrowser.open(
        "https://chatgpt.com"
    )

    dashboard = get_dashboard()

    return (
        "Hackathon workspace ready. "
        + dashboard
    )


def morning_briefing():

    briefing = []

    briefing.append("Good morning Abir.")

    briefing.append(get_date())
    briefing.append(get_time())

    briefing.append(get_battery_status())

    briefing.append(get_system_info())

    briefing.append(status_report())

    return "\n".join(briefing)

# ======================
# OCR READER
# ======================

def read_image_text(filename):

    from ocr_reader import read_text_from_image

    return read_text_from_image(filename)

def read_current_screen():

    from vision import capture_screen
    from ocr_reader import read_text_from_image

    image = capture_screen()

    return read_text_from_image(image)

def analyze_current_screen():

    from vision import capture_screen
    from screen_analyzer import analyze_screen

    image = capture_screen()

    return analyze_screen(image)

# ======================
# FILE SEARCH
# ======================

def search_files(keyword):

    from file_search import find_file

    return find_file(keyword)

def open_file_by_name(keyword):

    from file_search import open_file

    return open_file(keyword)

# ======================
# CLOSE APPLICATIONS
# ======================

def close_app(app_name):
    processes = {
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "browser": "chrome.exe",
        "website": "chrome.exe",
        "vscode": "Code.exe",
        "vs code": "Code.exe",
        "notepad": "notepad.exe",
        "calculator": "CalculatorApp.exe"
    }

    app_name = app_name.lower().strip()

    if app_name in processes:

        os.system(
            f'taskkill /F /IM "{processes[app_name]}"'
        )

        return f"Closing {app_name}"

    return f"I don't know how to close {app_name}"

def open_folder_by_name(keyword):

    from file_search import open_folder

    return open_folder(keyword)

# ======================
# SYSTEM CONTROL
# ======================

def lock_computer():

    os.system(
        "rundll32.exe user32.dll,LockWorkStation"
    )

    return "Locking computer."

def volume_up():

    for _ in range(10):
        os.system(
            "powershell (New-Object -ComObject WScript.Shell).SendKeys([char]175)"
        )

    return "Volume increased."


def volume_down():

    for _ in range(10):
        os.system(
            "powershell (New-Object -ComObject WScript.Shell).SendKeys([char]174)"
        )

    return "Volume decreased."


def mute_volume():

    os.system(
        "powershell (New-Object -ComObject WScript.Shell).SendKeys([char]173)"
    )

    return "Volume muted."

def shutdown_pc():

    os.system("shutdown /s /t 0")

    return "Shutting down computer."


def restart_pc():

    os.system("shutdown /r /t 0")

    return "Restarting computer."


def sleep_pc():

    os.system(
        "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
    )

    return "Putting computer to sleep."

def open_any_app(app_name):

    from app_launcher import open_app

    return open_app(app_name)

def status_report():

    from memory_manager import (
        get_stats
    )

    stats = get_stats()

    report = []

    report.append(
        f"Projects: {stats['projects']}"
    )

    report.append(
        f"Goals: {stats['goals']}"
    )

    report.append(
        f"Skills: {stats['skills']}"
    )

    report.append(
        f"Notes: {stats['notes']}"
    )

    report.append(
       f"Tasks: {stats['tasks']}"
    )

    return "\n".join(report)

def end_of_day_review():

    from memory_manager import (
        load_memory
    )

    memory = load_memory()

    tasks = len(
        memory.get("tasks", [])
    )

    goals = len(
        memory.get("goals", [])
    )

    projects = len(
        memory.get("projects", [])
    )

    return (
        f"End of Day Review\n\n"
        f"Tasks: {tasks}\n"
        f"Goals: {goals}\n"
        f"Projects: {projects}\n\n"
        f"What did you accomplish today?"
    )


