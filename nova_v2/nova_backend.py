import sys
import os

# Ensure NOVA root is in path so we can import the existing backend modules
NOVA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if NOVA_ROOT not in sys.path:
    sys.path.insert(0, NOVA_ROOT)


class NovaBackend:
    """Bridge between the NOVA v2 GUI and the existing backend modules."""

    def __init__(self):
        self.pending_action = None
        self.pending_action_type = None

        # Lazy imports so the GUI can start even if Ollama isn't running yet
        self._get_response = None
        self._get_stream_response = None
        self._set_ai_model = None

    def set_ai_model(self, model_name: str):
        from ai_brain import set_ai_model
        set_ai_model(model_name)

    # ------------------------------------------------------------------
    # AI / chat
    # ------------------------------------------------------------------
    def _import_ai(self):
        if self._get_response is None:
            from nova_brain import get_response, get_stream_response  # noqa
            self._get_response = get_response
            self._get_stream_response = get_stream_response

    def get_response(self, text: str) -> str:
        self._import_ai()
        return self._get_response(text)

    def get_stream_response(self, text: str):
        """Yields chunks of AI response text (streaming)."""
        self._import_ai()
        for chunk in self._get_stream_response(text):
            yield chunk

    # ------------------------------------------------------------------
    # Memory / productivity
    # ------------------------------------------------------------------
    def load_memory(self):
        from memory_manager import load_memory
        return load_memory()

    def save_memory(self, memory):
        from memory_manager import save_memory
        save_memory(memory)

    def get_stats(self):
        from memory_manager import get_stats
        return get_stats()

    def about_user(self):
        from memory_manager import about_user
        return about_user()

    def daily_plan(self):
        from memory_manager import daily_plan
        return daily_plan()

    def end_of_day_review(self):
        from memory_manager import end_of_day_review
        return end_of_day_review()

    # Projects
    def add_project(self, project: str) -> str:
        from memory_manager import add_project
        return add_project(project)

    def list_projects_memory(self) -> str:
        from memory_manager import list_projects_memory
        return list_projects_memory()

    def show_project(self, project: str) -> str:
        from memory_manager import show_project
        return show_project(project)

    def add_project_note(self, project: str, note: str) -> str:
        from memory_manager import add_project_note
        return add_project_note(project, note)

    def delete_project_note(self, project: str, index: int) -> str:
        from memory_manager import delete_project_note
        return delete_project_note(project, index)

    # Skills
    def add_skill(self, skill: str) -> str:
        from memory_manager import add_skill
        return add_skill(skill)

    def list_skills(self) -> str:
        from memory_manager import list_skills
        return list_skills()

    # Goals
    def add_goal(self, goal: str) -> str:
        from memory_manager import add_goal
        return add_goal(goal)

    def list_goals(self) -> str:
        from memory_manager import list_goals
        return list_goals()

    # Notes
    def add_note(self, note: str) -> str:
        from memory_manager import add_note
        return add_note(note)

    def list_notes(self) -> str:
        from memory_manager import list_notes
        return list_notes()

    def search_notes(self, keyword: str) -> str:
        from memory_manager import search_notes
        return search_notes(keyword)

    def delete_note(self, index: int) -> str:
        from memory_manager import delete_note
        return delete_note(index)

    # Tasks
    def add_task(self, task: str) -> str:
        from memory_manager import add_task
        return add_task(task)

    def list_tasks(self) -> str:
        from memory_manager import list_tasks
        return list_tasks()

    def complete_task(self, index: int) -> str:
        from memory_manager import complete_task
        return complete_task(index)

    def delete_task(self, index: int) -> str:
        from memory_manager import delete_task
        return delete_task(index)

    # Journal
    def add_journal_entry(self, entry: str) -> str:
        from memory_manager import add_journal_entry
        return add_journal_entry(entry)

    def show_journal(self) -> str:
        from memory_manager import show_journal
        return show_journal()

    def delete_journal_entry(self, index: int) -> str:
        from memory_manager import delete_journal_entry
        return delete_journal_entry(index)

    # ------------------------------------------------------------------
    # Actions / automation
    # ------------------------------------------------------------------
    def open_youtube(self) -> str:
        from actions import open_youtube
        return open_youtube()

    def open_google(self) -> str:
        from actions import open_google
        return open_google()

    def open_github(self) -> str:
        from actions import open_github
        return open_github()

    def search_google(self, query: str) -> str:
        from actions import search_google
        return search_google(query)

    def search_youtube(self, query: str) -> str:
        from actions import search_youtube
        return search_youtube(query)

    def open_website(self, url: str) -> str:
        from actions import open_website
        return open_website(url)

    def open_notepad(self) -> str:
        from actions import open_notepad
        return open_notepad()

    def open_calculator(self) -> str:
        from actions import open_calculator
        return open_calculator()

    def open_vscode(self) -> str:
        from actions import open_vscode
        return open_vscode()

    def open_chrome(self) -> str:
        from actions import open_chrome
        return open_chrome()

    def open_downloads(self) -> str:
        from actions import open_downloads
        return open_downloads()

    def open_documents(self) -> str:
        from actions import open_documents
        return open_documents()

    def open_desktop(self) -> str:
        from actions import open_desktop
        return open_desktop()

    def open_file_explorer(self) -> str:
        from actions import open_file_explorer
        return open_file_explorer()

    def take_screenshot(self) -> str:
        from actions import take_screenshot
        return take_screenshot()

    def create_text_file(self, filename: str) -> str:
        from actions import create_text_file
        return create_text_file(filename)

    def create_python_file(self, filename: str) -> str:
        from actions import create_python_file
        return create_python_file(filename)

    def create_folder(self, foldername: str) -> str:
        from actions import create_folder
        return create_folder(foldername)

    def create_python_project(self, project_name: str) -> str:
        from actions import create_python_project
        return create_python_project(project_name)

    def start_project(self, project_name: str) -> str:
        from actions import start_project
        return start_project(project_name)

    def work_on_project(self, project_name: str) -> str:
        from actions import work_on_project
        return work_on_project(project_name)

    def list_projects(self) -> str:
        from actions import list_projects
        return list_projects()

    def open_project(self, project_name: str) -> str:
        from actions import open_project
        return open_project(project_name)

    def get_time(self) -> str:
        from actions import get_time
        return get_time()

    def get_date(self) -> str:
        from actions import get_date
        return get_date()

    def get_battery_status(self) -> str:
        from actions import get_battery_status
        return get_battery_status()

    def get_system_info(self) -> str:
        from actions import get_system_info
        return get_system_info()

    def read_chat_history(self) -> str:
        from actions import read_chat_history
        return read_chat_history()

    def start_coding(self) -> str:
        from actions import start_coding
        return start_coding()

    def hackathon_mode(self) -> str:
        from actions import hackathon_mode
        return hackathon_mode()

    def study_mode(self) -> str:
        from actions import study_mode
        return study_mode()

    def hackathon_setup(self) -> str:
        from actions import hackathon_setup
        return hackathon_setup()

    def morning_briefing(self) -> str:
        from actions import morning_briefing
        return morning_briefing()

    def status_report(self) -> str:
        from actions import status_report
        return status_report()

    # System control (with confirmation)
    def lock_computer(self) -> str:
        from actions import lock_computer
        return lock_computer()

    def shutdown_pc(self) -> str:
        from actions import shutdown_pc
        return shutdown_pc()

    def restart_pc(self) -> str:
        from actions import restart_pc
        return restart_pc()

    def sleep_pc(self) -> str:
        from actions import sleep_pc
        return sleep_pc()

    def volume_up(self) -> str:
        from actions import volume_up
        return volume_up()

    def volume_down(self) -> str:
        from actions import volume_down
        return volume_down()

    def mute_volume(self) -> str:
        from actions import mute_volume
        return mute_volume()

    def close_app(self, app_name: str) -> str:
        from actions import close_app
        return close_app(app_name)

    def search_files(self, keyword: str) -> str:
        from actions import search_files
        return search_files(keyword)

    def open_file_by_name(self, keyword: str) -> str:
        from actions import open_file_by_name
        return open_file_by_name(keyword)

    def open_folder_by_name(self, keyword: str) -> str:
        from actions import open_folder_by_name
        return open_folder_by_name(keyword)

    def read_image_text(self, filename: str) -> str:
        from actions import read_image_text
        return read_image_text(filename)

    def read_current_screen(self) -> str:
        from actions import read_current_screen
        return read_current_screen()

    def analyze_current_screen(self) -> str:
        from actions import analyze_current_screen
        return analyze_current_screen()

    def generate_python_program(self, filename: str, prompt: str) -> str:
        from actions import generate_python_program
        return generate_python_program(filename, prompt)

    def improve_python_file(self, filename: str) -> str:
        from actions import improve_python_file
        return improve_python_file(filename)

    def explain_python_file(self, filename: str) -> str:
        from actions import explain_python_file
        return explain_python_file(filename)

    def generate_project_readme(self, project_name: str) -> str:
        from actions import generate_project_readme
        return generate_project_readme(project_name)

    def find_bugs_in_file(self, filename: str) -> str:
        from actions import find_bugs_in_file
        return find_bugs_in_file(filename)

    def fix_python_file(self, filename: str) -> str:
        from actions import fix_python_file
        return fix_python_file(filename)

    # ------------------------------------------------------------------
    # Voice
    # ------------------------------------------------------------------
    def speak(self, text: str):
        from nova_voice import speak
        speak(text)

    def listen(self) -> str:
        from listen import listen
        return listen()
