import json

MEMORY_FILE = "memory.json"


def load_memory():

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            memory = json.load(f)

    except:

        memory = {
            "user": {
                "name": "Abir",
                "preferences": {}
            },
            "facts": [],
            "projects": [],
            "skills": [],
            "goals": [],
            "notes": [],
            "tasks":[]
        }

    memory.setdefault("facts", [])
    memory.setdefault("projects", [])
    memory.setdefault("skills", [])
    memory.setdefault("goals", [])
    memory.setdefault("notes", [])

    return memory


def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            indent=4
        )


def get_memory_context():

    memory = load_memory()

    facts = memory.get("facts", [])

    if not facts:
        return ""

    return (
        "Known facts about the user:\n"
        + "\n".join(facts)
    )


def add_project(project):

    memory = load_memory()

    if project not in memory["projects"]:
        memory["projects"].append(project)
        save_memory(memory)

    return f"Project added: {project}"


def list_projects_memory():

    memory = load_memory()

    projects = memory["projects"]

    if not projects:
        return "No projects stored."

    return ", ".join(projects)


def add_skill(skill):

    memory = load_memory()

    if skill not in memory["skills"]:
        memory["skills"].append(skill)
        save_memory(memory)

    return f"Skill added: {skill}"


def list_skills():

    memory = load_memory()

    skills = memory["skills"]

    if not skills:
        return "No skills stored."

    return ", ".join(skills)


def add_goal(goal):

    memory = load_memory()

    if goal not in memory["goals"]:
        memory["goals"].append(goal)
        save_memory(memory)

    return f"Goal added: {goal}"


def list_goals():

    memory = load_memory()

    goals = memory["goals"]

    if not goals:
        return "No goals stored."

    return ", ".join(goals)


def add_note(note):

    memory = load_memory()

    memory["notes"].append(note)

    save_memory(memory)

    return "Note saved."


def list_notes():

    memory = load_memory()

    notes = memory["notes"]

    if not notes:
        return "No notes found."

    result = []

    for i, note in enumerate(notes, start=1):
        result.append(f"{i}. {note}")

    return "\n".join(result)


def search_notes(keyword):

    memory = load_memory()

    notes = memory["notes"]

    matches = []

    for note in notes:

        if keyword.lower() in note.lower():
            matches.append(note)

    if not matches:
        return "No matching notes found."

    return "\n".join(matches)


def delete_note(index):

    memory = load_memory()

    notes = memory["notes"]

    if index < 1 or index > len(notes):
        return "Invalid note number."

    removed = notes.pop(index - 1)

    save_memory(memory)

    return f"Deleted note: {removed}"

# ======================
# TASKS
# ======================

def add_task(task):

    memory = load_memory()

    memory["tasks"].append(
        {
            "text": task,
            "completed": False
        }
    )

    save_memory(memory)

    return "Task added."


def list_tasks():

    memory = load_memory()

    tasks = memory.get("tasks", [])

    if not tasks:
        return "No tasks found."

    result = []

    for i, task in enumerate(tasks, start=1):

        status = "☑" if task["completed"] else "☐"

        result.append(
            f"{i}. {status} {task['text']}"
        )

    return "\n".join(result)


def complete_task(index):

    memory = load_memory()

    tasks = memory.get("tasks", [])

    if index < 1 or index > len(tasks):
        return "Invalid task number."

    tasks[index - 1]["completed"] = True

    save_memory(memory)

    return "Task completed."


def delete_task(index):

    memory = load_memory()

    tasks = memory.get("tasks", [])

    if index < 1 or index > len(tasks):
        return "Invalid task number."

    removed = tasks.pop(index - 1)

    save_memory(memory)

    return f"Deleted task: {removed['text']}"


def get_dashboard():

    memory = load_memory()

    projects = memory["projects"]
    goals = memory["goals"]

    result = ""

    if projects:
        result += (
            "Projects: "
            + ", ".join(projects)
            + ". "
        )

    if goals:
        result += (
            "Goals: "
            + ", ".join(goals)
            + "."
        )

    return result


def about_user():

    memory = load_memory()

    name = memory["user"].get(
        "name",
        "Unknown"
    )

    projects = memory["projects"]
    skills = memory["skills"]
    goals = memory["goals"]
    facts = memory["facts"]

    summary = f"Your name is {name}. "

    if projects:
        summary += (
            "Projects: "
            + ", ".join(projects)
            + ". "
        )

    if skills:
        summary += (
            "Skills: "
            + ", ".join(skills)
            + ". "
        )

    if goals:
        summary += (
            "Goals: "
            + ", ".join(goals)
            + ". "
        )

    if facts:
        summary += (
            "I remember: "
            + ", ".join(facts)
            + "."
        )

    return summary

def add_project_note(project, note):

    memory = load_memory()

    project_notes = memory.get(
        "project_notes",
        {}
    )

    if project not in project_notes:
        project_notes[project] = []

    project_notes[project].append(note)

    memory["project_notes"] = project_notes

    save_memory(memory)

    return f"Added note to {project}"

def show_project(project):

    memory = load_memory()

    project_notes = memory.get(
        "project_notes",
        {}
    )

    notes = project_notes.get(
        project,
        []
    )

    if not notes:
        return f"No notes found for {project}"

    result = [f"Project: {project}"]

    for i, note in enumerate(notes, start=1):
        result.append(f"{i}. {note}")

    return "\n".join(result)

def delete_project_note(project, index):

    memory = load_memory()

    project_notes = memory.get(
        "project_notes",
        {}
    )

    notes = project_notes.get(
        project,
        []
    )

    if index < 1 or index > len(notes):
        return "Invalid note number."

    removed = notes.pop(index - 1)

    save_memory(memory)

    return f"Deleted: {removed}"

def add_journal_entry(entry):

    memory = load_memory()

    memory["journal"].append(entry)

    save_memory(memory)

    return "Journal entry saved."


def show_journal():

    memory = load_memory()

    journal = memory.get(
        "journal",
        []
    )

    if not journal:
        return "No journal entries."

    result = []

    for i, entry in enumerate(
        journal,
        start=1
    ):

        result.append(
            f"{i}. {entry}"
        )

    return "\n".join(result)

def delete_journal_entry(index):

    memory = load_memory()

    journal = memory.get(
        "journal",
        []
    )

    if index < 1 or index > len(journal):

        return "Invalid entry number."

    removed = journal.pop(index - 1)

    save_memory(memory)

    return f"Deleted journal entry: {removed}"