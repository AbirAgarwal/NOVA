import json

MEMORY_FILE = "memory.json"


def get_memory_context():

    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)

        facts = memory.get("facts", [])

        if not facts:
            return ""

        return "Known facts about the user:\n" + "\n".join(facts)

    except:
        return ""