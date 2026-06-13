# NOVA v1.0

NOVA is a local AI-powered desktop assistant built in Python.

It combines voice interaction, local AI models, memory, automation, project generation, and coding assistance into a single personal assistant.

## Features

### Voice Assistant

* Voice input using Speech Recognition
* Female voice output using pyttsx3
* Wake word support ("Nova")

### Local AI

* Powered by Ollama
* Uses Qwen3 1.7B locally
* No cloud API required

### Memory System

* Remembers user facts
* Stores memory in memory.json
* Memory-aware AI conversations

### Chat History

* Saves conversations to chat_history.txt
* Can recall recent conversations

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

### Screenshot System

* Capture screenshots
* Automatically save screenshots

### File Management

* Create text files
* Create Python files
* Create folders

### Project Generation

* Generate Python project structures
* Create README files
* Create requirements.txt

### AI Coding Assistant

* Generate Python programs
* Improve existing Python files
* Refactor code using local AI

## Technologies Used

* Python
* Ollama
* Qwen3 1.7B
* pyttsx3
* SpeechRecognition
* Tkinter
* psutil
* Pillow

## Project Structure

NOVA/
├── actions.py
├── ai_brain.py
├── code_editor.py
├── project_assistant.py
├── memory_manager.py
├── nova_brain.py
├── nova_voice.py
├── nova_gui.py
├── vision.py
├── listen.py
├── memory.json
├── chat_history.txt
├── README.md
└── devlog.md

## Future Plans

* Vision AI
* Screen Understanding
* Better GUI
* Multi-Step Task Execution
* Personal Knowledge Base
* Advanced Automation

Version: v1.0
Author: Abir Agarwal
