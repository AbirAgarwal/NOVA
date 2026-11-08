"""
NOVA Backend Server
Provides API endpoints for the HTML/JARVIS frontend.
Connects to the existing NOVA backend modules (ai_brain, nova_brain, memory_manager, etc.)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add NOVA directory to path so we can import existing modules
NOVA_DIR = os.path.dirname(os.path.abspath(__file__))
if NOVA_DIR not in sys.path:
    sys.path.insert(0, NOVA_DIR)

# Import existing NOVA backend modules
from ai_brain import get_ai_response, stream_ai_response, set_ai_model, AI_MODEL
from nova_brain import get_response, get_stream_response
from memory_manager import get_stats, load_memory, save_memory, show_notification
from actions import (
    open_youtube, open_google, open_github, search_google, search_youtube,
    open_website, open_notepad, open_calculator, open_vscode, open_chrome,
    open_downloads, open_documents, open_desktop, open_file_explorer,
    take_screenshot, create_text_file, create_python_file, create_folder,
    create_python_project, start_project, work_on_project, list_projects,
    open_project, get_time, get_date, get_battery_status, get_system_info,
    read_chat_history, start_coding, hackathon_mode, study_mode, hackathon_setup,
    morning_briefing, status_report, volume_up, volume_down, mute_volume,
    lock_computer, shutdown_pc, restart_pc, sleep_pc, close_app, search_files,
    open_file_by_name, open_folder_by_name, read_image_text, read_current_screen,
    analyze_current_screen, generate_python_program, improve_python_file,
    explain_python_file, generate_project_readme, find_bugs_in_file,
    fix_python_file, status_report as get_status_report, end_of_day_review,
    add_project, list_projects_memory, add_skill, add_goal, add_note, add_task,
    complete_task, delete_task, add_journal_entry, show_journal,
    delete_journal_entry, add_project_note, show_project, delete_project_note,
    list_notes, search_notes, delete_note, list_skills, list_goals, about_user,
    daily_plan
)
from nova_voice import speak
from listen import listen

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the HTML frontend


# ======================
# CHAT ENDPOINT
# ======================

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat messages from the frontend."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'response': 'Please enter a message.'}), 400

        # Check for exit command
        if text.lower() in ('exit nova', 'close nova', 'shutdown nova', 'terminate nova'):
            return jsonify({'response': 'Shutting down NOVA.'})

        # Get response from NOVA brain (handles commands + AI fallback)
        response = get_response(text)

        return jsonify({'response': response})

    except Exception as exc:
        return jsonify({'response': f'Error: {str(exc)}'}), 500


# ======================
# MEMORY ENDPOINTS
# ======================

@app.route('/api/memory/stats', methods=['GET'])
def api_memory_stats():
    """Get memory statistics."""
    try:
        stats = get_stats()
        return jsonify(stats)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/about', methods=['GET'])
def api_memory_about():
    """Get user information."""
    try:
        info = about_user()
        return jsonify({'info': info})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/projects', methods=['GET'])
def api_list_projects():
    """List stored projects."""
    try:
        result = list_projects_memory()
        return jsonify({'projects': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/projects', methods=['POST'])
def api_add_project():
    """Add a project."""
    try:
        data = request.get_json()
        name = data.get('name', '')
        if not name:
            return jsonify({'error': 'Project name required'}), 400
        result = add_project(name)
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/tasks', methods=['GET'])
def api_list_tasks():
    """List tasks."""
    try:
        from memory_manager import list_tasks
        result = list_tasks()
        return jsonify({'tasks': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/tasks', methods=['POST'])
def api_add_task():
    """Add a task."""
    try:
        data = request.get_json()
        task = data.get('task', '')
        if not task:
            return jsonify({'error': 'Task required'}), 400
        result = add_task(task)
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/notes', methods=['GET'])
def api_list_notes():
    """List notes."""
    try:
        from memory_manager import list_notes
        result = list_notes()
        return jsonify({'notes': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/notes', methods=['POST'])
def api_add_note():
    """Add a note."""
    try:
        data = request.get_json()
        note = data.get('note', '')
        if not note:
            return jsonify({'error': 'Note required'}), 400
        result = add_note(note)
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/skills', methods=['GET'])
def api_list_skills():
    """List skills."""
    try:
        from memory_manager import list_skills
        result = list_skills()
        return jsonify({'skills': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/goals', methods=['GET'])
def api_list_goals():
    """List goals."""
    try:
        from memory_manager import list_goals
        result = list_goals()
        return jsonify({'goals': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/memory/journal', methods=['GET'])
def api_list_journal():
    """List journal entries."""
    try:
        from memory_manager import show_journal
        result = show_journal()
        return jsonify({'journal': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ======================
# SYSTEM ENDPOINTS
# ======================

@app.route('/api/system/time', methods=['GET'])
def api_system_time():
    """Get current time."""
    try:
        result = get_time()
        return jsonify({'result': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/system/date', methods=['GET'])
def api_system_date():
    """Get current date."""
    try:
        result = get_date()
        return jsonify({'result': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/system/battery', methods=['GET'])
def api_system_battery():
    """Get battery status."""
    try:
        result = get_battery_status()
        return jsonify({'result': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/system/info', methods=['GET'])
def api_system_info():
    """Get system info."""
    try:
        result = get_system_info()
        return jsonify({'result': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/system/status', methods=['GET'])
def api_system_status():
    """Get status report."""
    try:
        result = get_status_report()
        return jsonify({'result': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/system/briefing', methods=['GET'])
def api_system_briefing():
    """Get morning briefing."""
    try:
        result = morning_briefing()
        return jsonify({'result': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/system/plan', methods=['GET'])
def api_system_plan():
    """Get daily plan."""
    try:
        result = daily_plan()
        return jsonify({'result': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/system/review', methods=['GET'])
def api_system_review():
    """Get end of day review."""
    try:
        result = end_of_day_review()
        return jsonify({'result': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ======================
# ACTION ENDPOINTS
# ======================

@app.route('/api/action/open-youtube', methods=['POST'])
def api_open_youtube():
    try:
        result = open_youtube()
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/open-google', methods=['POST'])
def api_open_google():
    try:
        result = open_google()
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/open-github', methods=['POST'])
def api_open_github():
    try:
        result = open_github()
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/search-google', methods=['POST'])
def api_search_google():
    try:
        data = request.get_json()
        query = data.get('query', '')
        result = search_google(query)
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/open-website', methods=['POST'])
def api_open_website():
    try:
        data = request.get_json()
        url = data.get('url', '')
        result = open_website(url)
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/open-notepad', methods=['POST'])
def api_open_notepad():
    try:
        result = open_notepad()
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/open-calculator', methods=['POST'])
def api_open_calculator():
    try:
        result = open_calculator()
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/open-vscode', methods=['POST'])
def api_open_vscode():
    try:
        result = open_vscode()
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/open-chrome', methods=['POST'])
def api_open_chrome():
    try:
        result = open_chrome()
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/take-screenshot', methods=['POST'])
def api_take_screenshot():
    try:
        result = take_screenshot()
        return jsonify({'response': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@app.route('/api/action/voice-speak', methods=['POST'])
def api_voice_speak():
    try:
        data = request.get_json()
        text = data.get('text', '')
        speak(text)
        return jsonify({'response': 'Spoken.'})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ======================
# AI MODEL ENDPOINT
# ======================

@app.route('/api/ai/model', methods=['POST'])
def api_ai_model():
    """Set the AI model."""
    try:
        data = request.get_json()
        model = data.get('model', 'qwen3:1.8b')
        set_ai_model(model)
        return jsonify({'response': f'AI model set to {model}'})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ======================
# HEALTH CHECK
# ======================

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'online', 'ai_model': AI_MODEL})


if __name__ == '__main__':
    print("=" * 60)
    print("NOVA Backend Server")
    print("=" * 60)
    print("Starting on http://localhost:8765")
    print("Open nova.html in your browser to use the interface")
    print("=" * 60)
    app.run(host='127.0.0.1', port=8765, debug=False)
