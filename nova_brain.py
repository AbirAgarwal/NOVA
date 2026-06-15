import json
from ai_brain import get_ai_response
from actions import *
from memory_manager import *
from actions import hackathon_setup
from actions import morning_briefing


MEMORY_FILE = "memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "user": {
                "name": "Abir",
                "preferences": {}
            },
            "facts": []
        }


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


memory = load_memory()


def get_response(text):

    global memory

    text = text.lower()

    name = memory["user"].get("name", "Abir")

    # ======================
    # MEMORY COMMANDS
    # ======================

    if "hello" in text:
        return f"Hello {name}. I am NOVA."

    if "my name is" in text:
        new_name = text.replace("my name is", "").strip()

        memory["user"]["name"] = new_name

        save_memory(memory)

        return f"Got it. I will remember your name is {new_name}"

    if "what is my name" in text:
        return f"Your name is {memory['user'].get('name', 'unknown')}"

    if "remember that" in text:

        fact = text.replace("remember that", "").strip()

        if fact not in memory["facts"]:

            memory["facts"].append(fact)

            save_memory(memory)

            return "Noted. I will remember that."

        return "I already remember that."

    if "what do you remember" in text:

        if not memory["facts"]:
            return "I don't remember anything yet."

        recent = memory["facts"][-5:]

        formatted = "; ".join(recent)

        return f"You told me: {formatted}"

    # ======================
    # WEBSITE COMMANDS
    # ======================

    if "open youtube" in text:
        return open_youtube()

    if "open google" in text:
        return open_google()

    if "open github" in text:
        return open_github()

    if "search google for" in text:

        query = text.replace(
            "search google for",
            ""
        ).strip()

        return search_google(query)

    if "search youtube for" in text:

        query = text.replace(
            "search youtube for",
            ""
        ).strip()

        return search_youtube(query)

    # ======================
    # APPLICATION COMMANDS
    # ======================

    if "open chrome" in text:
        return open_chrome()

    if "open notepad" in text:
        return open_notepad()

    if "open calculator" in text:
        return open_calculator()

    if (
        "open vscode" in text
        or "open vs code" in text
        or "open versus code" in text
        or "open visual studio code" in text
    ):
        return open_vscode()

    # ======================
    # FOLDER COMMANDS
    # ======================

    if "open downloads" in text:
        return open_downloads()

    if "open documents" in text:
        return open_documents()

    if "open desktop" in text:
        return open_desktop()

    if "open file explorer" in text:
        return open_file_explorer()

    # ======================
    # SCREENSHOT
    # ======================

    if "take screenshot" in text:
        return take_screenshot()

    # ======================
    # FILE COMMANDS
    # ======================

    if "create text file" in text:

        filename = text.replace(
            "create text file",
            ""
        ).strip()

        return create_text_file(filename)

    if "create python file" in text:

        filename = text.replace(
            "create python file",
            ""
        ).strip()

        return create_python_file(filename)

    if "create folder" in text:

        foldername = text.replace(
            "create folder",
            ""
        ).strip()

        return create_folder(foldername)

    if "create python project" in text:

        project_name = text.replace(
            "create python project",
            ""
        ).strip()

        return create_python_project(project_name)

    # ======================
    # SYSTEM COMMANDS
    # ======================

    if "what time" in text:
        return get_time()

    if "date" in text:
        return get_date()

    if "battery status" in text:
        return get_battery_status()

    if "system info" in text:
        return get_system_info()

    #=================
    # CHAT HISTORY
    #=================
    if "chat history" in text:
        return read_chat_history()
    
    if "generate calculator program" in text:
        return generate_python_program(
            "calculator.py",
            "Create a calculator program"
        )

    if "improve file" in text:

        filename = text.replace(
            "improve file",
            ""
        ).strip()

        return improve_python_file(filename)
    
    if "start coding" in text:
        return start_coding()

    if "hackathon mode" in text:
        return hackathon_mode()

    if "study mode" in text:
        return study_mode()
    
    
    if "list project" in text or "list projects" in text:
        return list_projects()


    if "open project" in text:

        project_name = text.replace(
            "open project",
            ""
        ).strip()

        return open_project(project_name)
    
    if "explain file" in text:

        filename = text.replace(
            "explain file",
            ""
        ).strip()

        return explain_python_file(filename)
    
    if "generate readme for" in text or "generate read me for" in text:

        project_name = text.replace(
            "generate readme for",
            ""
        ).strip()

        return generate_project_readme(
            project_name
        )
    
    if  ("find bug in file" in text or "find bugs in file" in text):

        filename = text.replace(
            "find bugs in file",
            ""
        ).strip()

        return find_bugs_in_file(filename)
    
    if "fix file" in text:

        filename = text.replace(
            "fix file",
            ""
        ).strip()

        return fix_python_file(filename)

    if "add project" in text:

        project = text.replace(
            "add project",
            ""
        ).strip()

        return add_project(project)

    if "add skill" in text:

        skill = text.replace(
            "add skill",
            ""
        ).strip()

        return add_skill(skill)

    if "add goal" in text:

        goal = text.replace(
            "add goal",
            ""
        ).strip()

        return add_goal(goal)

    if ("list my project" in text or "list my projects" in text):
        return list_projects_memory()

    if ("list my skills" in text or "lis my skill" in text ):
        return list_skills()

    if ("list my goals" in text or "list my goal" in text) :
        return list_goals()

    if ("tell me about myself" in text or "who am i" in text):
        return about_user()
    
    if "start project" in text:

        project_name = text.replace(
            "start project",
            ""
        ).strip()

        return start_project(project_name)
    
    if "hackathon setup" in text:
        return hackathon_setup()
    
    if "morning briefing" in text or "morning brief" in text:
        return morning_briefing()

    if "daily briefing" in text or "daily brief" in text:
        return morning_briefing()
    
    if "save note" in text or "save notes" in text:

        note = text.replace(
            "save note",
            ""
        ).strip()

        return add_note(note)
    
    if "show notes" in text or "show note" in text:
        return list_notes()
    
    if "search notes" in text or "search note" in text:

        keyword = text.replace(
            "search notes",
            ""
        ).strip()

        return search_notes(keyword)
    
    if "delete note" in text:

        try:

            number = int(
                text.replace(
                    "delete note",
                    ""
                ).strip()
            )

            return delete_note(number)

        except:

            return "Please provide a note number."
        
    if "add task" in text or "add tasks" in text:

        task = text.replace(
            "add task",
            ""
        ).strip()

        return add_task(task)
    
    if "show tasks" in text or "show task" in text:
        return list_tasks()

    if "complete task" in text:

        try:

            number = int(
                text.replace(
                    "complete task",
                    ""
                ).strip()
            )

            return complete_task(number)

        except:

            return "Please provide a task number."
        
    if "delete task" in text:

        try:

            number = int(
                text.replace(
                    "delete task",
                    ""
                ).strip()
            )

            return delete_task(number)

        except:

            return "Please provide a task number."

    if "project note" in text:

        content = text.replace(
            "project note",
            ""
        ).strip()

        parts = content.split(" ", 1)

        if len(parts) < 2:
            return "Please provide project and note."

        project = parts[0]
        note = parts[1]

        return add_project_note(
            project,
            note
        )
    
    if "show project" in text:

        project = text.replace(
            "show project",
            ""
        ).strip()

        return show_project(project)
    
    if "delete project note" in text:

        try:

            content = text.replace(
                "delete project note",
                ""
            ).strip()

            parts = content.split()

            project = parts[0]

            number = int(parts[1])

            return delete_project_note(
                project,
                number
            )

        except:

            return (
                "Use: delete project note "
                "project_name note_number"
            )
    
    if "journal today" in text:

        entry = text.replace(
            "journal today",
            ""
        ).strip()

        return add_journal_entry(entry)

    if "show journal" in text:
        return show_journal()

    if "delete journal" in text:

        try:

            number = int(
                text.replace(
                    "delete journal",
                    ""
                ).strip()
            )

            return delete_journal_entry(
                number
            )

        except:

            return (
                "Please provide "
                "a journal number."
            )
        
    # ======================
    # OCR COMMANDS
    # ======================

    if "read image" in text:

        filename = text.replace(
            "read image",
            ""
        ).strip()

        return read_image_text(filename)
    
    if "read my screen" in text:
        return read_current_screen()

    if "what is on my screen" in text:
        return analyze_current_screen()

    if "analyze my screen" in text or "analyse my screen" in text:
        return analyze_current_screen()

    # ======================
    # AI FALLBACK
    # ======================

    return get_ai_response(text)
