import json

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
        if not recent:
            return "I don't remember anything yet."

        formatted = "; ".join(recent)
        return f"You told me: {formatted}"

    # default
    return "I am still learning."