# NOVA v1.2

NOVA is a local AI-powered desktop assistant built in Python.

It combines voice interaction, local AI models, memory, productivity tools, project management, automation, and coding assistance into a single personal AI operating companion.

## Features

### Voice Assistant

* Voice input using Speech Recognition
* Female voice output using pyttsx3
* Wake word support ("Nova")
* Real-time conversation interface

### Local AI

* Powered by Ollama
* Uses Qwen3 1.7B locally
* No cloud API required
* Context-aware conversations

### Memory System

* Remembers user facts
* Stores projects
* Stores goals
* Stores skills
* Stores notes
* Stores tasks
* Stores journal entries
* Stores project-specific notes

### Productivity System

#### Notes

* Save notes
* View notes
* Search notes
* Delete notes

#### Tasks

* Add tasks
* View tasks
* Complete tasks
* Delete tasks

#### Journal

* Daily journal entries
* View journal history
* Delete journal entries

#### Goals

* Add goals
* View goals

#### Skills

* Add skills
* View skills

### Project Management

* Add projects
* View projects
* Open projects
* Start projects
* Project-specific notes
* Project progress tracking

### Desktop Automation

* Open Chrome
* Open VS Code
* Open Notepad
* Open Calculator
* Open Downloads
* Open Documents
* Open Desktop
* Open File Explorer

### Web Actions

* Open Google
* Open YouTube
* Open GitHub
* Search Google
* Search YouTube

### System Utilities

* Current Time
* Current Date
* Battery Status
* System Information
* Morning Briefing

### Screenshot System

* Capture screenshots
* Automatic screenshot storage

### File Management

* Create text files
* Create Python files
* Create folders

### Project Generation

* Generate Python project structures
* Create README files
* Create requirements.txt
* Open generated projects automatically

### AI Coding Assistant

* Generate Python programs
* Improve Python files
* Explain Python files
* Find bugs
* Fix code
* Refactor code using local AI

### Workspace Modes

#### Coding Mode

Opens:

* VS Code
* GitHub
* Chrome

#### Hackathon Mode

Opens:

* VS Code
* GitHub
* YouTube
* Project Dashboard

#### Study Mode

Opens:

* Google
* YouTube

## Technologies Used

* Python
* Ollama
* Qwen3 1.7B
* SpeechRecognition
* pyttsx3
* Tkinter
* psutil
* Pillow

## Project Structure

NOVA/
├── actions.py
├── ai_brain.py
├── bug_finder.py
├── code_editor.py
├── code_fixer.py
├── file_explainer.py
├── listen.py
├── main.py
├── memory_manager.py
├── nova_brain.py
├── nova_gui.py
├── nova_voice.py
├── project_assistant.py
├── readme_generator.py
├── vision.py
├── README.md
├── ROADMAP.md
└── devlog.md

## Future Plans

### v1.3

* Reminders
* Deadlines
* Better Project Tracking

### v1.4

* OCR
* Vision AI
* Screen Understanding

### v2.0

* Agent System
* Autonomous Planning
* Multi-Step Task Execution
* Advanced Automation

Version: v1.2

Author: Abir Agarwal

