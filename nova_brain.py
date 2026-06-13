import json

from ai_brain import get_ai_response

from actions import *

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
    
    # ======================
    # AI FALLBACK
    # ======================

    return get_ai_response(text)