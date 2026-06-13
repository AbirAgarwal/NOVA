import json
from ai_brain import get_ai_response
from actions import open_youtube, open_google, open_github
from actions import open_notepad, open_calculator
from actions import open_vscode, take_screenshot
MEMORY_FILE = "memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "user": {"name": "Abir", "preferences": {}},
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

    # 🧠 greeting
    if "hello" in text:
        return f"Hello {name}. I am NOVA."

    # 🧠 store name
    if "my name is" in text:
        new_name = text.replace("my name is", "").strip()
        memory["user"]["name"] = new_name
        save_memory(memory)
        return f"Got it. I will remember your name is {new_name}"

    # 🧠 recall name
    if "what is my name" in text:
        return f"Your name is {memory['user'].get('name', 'unknown')}"

    if "open youtube" in text:
        return open_youtube()

    if "open google" in text:
        return open_google()
    
    if "open github" in text:
        return open_github()
    
    if "open notepad" in text:
        return open_notepad()

    if "open calculator" in text:
        return open_calculator()
    
    if "open vscode" in text or "open vs code" in text or "open versus code" in text or "open visual studio code" in text:
        return open_vscode()
    
    if "take screenshot" in text:
        return take_screenshot()
    
    # 🧠 store facts
    if "remember that" in text:
        fact = text.replace("remember that", "").strip()
        
        if fact not in memory["facts"]:
            memory["facts"].append(fact)
            save_memory(memory)
            save_memory(memory)
            return "Noted. I will remember that."

    # 🧠 recall facts
    if "what do you remember" in text:
        if not memory["facts"]:
            return "I don't remember anything yet."

        recent = memory["facts"][-5:]
        formatted = "; ".join(recent)

        return f"You told me: {formatted}"

    # If no command matches, use AI
    return get_ai_response(text)