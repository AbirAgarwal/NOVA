import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import psutil
from datetime import datetime
from nova_voice import speak
from listen import listen
from nova_brain import get_response, get_stream_response
from memory_manager import get_stats, show_notification
import pystray
from PIL import Image
import keyboard
import gui_controller


# ======================
# THEME (Jarvis / Iron Man)
# ======================

BG_COLOR = "#0a0f1f"
PANEL_COLOR = "#121826"
ACCENT_COLOR = "#00ffff"      # Cyan neon
ACCENT_DIM = "#0088aa"
TEXT_COLOR = "#e8edf5"
TEXT_DIM = "#a8b3cf"
SUCCESS_COLOR = "#00ff9d"
THINKING_COLOR = "#f1c40f"
SPEAKING_COLOR = "#9b59b6"
OFFLINE_COLOR = "#e74c3c"
ONLINE_COLOR = "#00ff9d"

FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_STATUS = ("Segoe UI", 11, "bold")
FONT_CHAT = ("Consolas", 12)
FONT_BUTTON = ("Segoe UI", 10, "bold")


# ======================
# WINDOW
# ======================

root = tk.Tk()
root.iconbitmap("nova_icon.ico")
root.title("NOVA — JARVIS Interface")
root.geometry("1300x850")
root.configure(bg=BG_COLOR)
root.minsize(1100, 700)

gui_controller.GUI_ROOT = root

nova_running = False
current_ai_model = "qwen3:4b"


# ======================
# TITLE BAR
# ======================

title_frame = tk.Frame(root, bg=BG_COLOR)
title_frame.pack(pady=(15, 5))

title_label = tk.Label(
    title_frame,
    text="◉ NOVA CORE",
    font=FONT_TITLE,
    fg=ACCENT_COLOR,
    bg=BG_COLOR
)
title_label.pack(side="left")

version_label = tk.Label(
    title_frame,
    text="v1.5 — JARVIS Edition",
    font=("Segoe UI", 10),
    fg=TEXT_DIM,
    bg=BG_COLOR
)
version_label.pack(side="left", padx=(15, 0), pady=(8, 0))

# AI model selector
model_frame = tk.Frame(root, bg=BG_COLOR)
model_frame.pack(pady=(0, 10))

tk.Label(
    model_frame,
    text="AI Model:",
    font=("Segoe UI", 10),
    fg=TEXT_DIM,
    bg=BG_COLOR
).pack(side="left", padx=(0, 8))

ai_model_var = tk.StringVar(value=current_ai_model)
ai_model_combo = ttk.Combobox(
    model_frame,
    textvariable=ai_model_var,
    values=["qwen3:1.8b", "qwen3:4b", "phi3:mini", "gemma2:2b", "tinyllama"],
    state="readonly",
    width=18,
    font=("Segoe UI", 10)
)
ai_model_combo.pack(side="left")


def on_model_change(event=None):
    global current_ai_model
    current_ai_model = ai_model_var.get()


ai_model_combo.bind("<<ComboboxSelected>>", on_model_change)


# ======================
# STATUS
# ======================

status_label = tk.Label(
    root,
    text="● OFFLINE",
    font=FONT_STATUS,
    fg=OFFLINE_COLOR,
    bg=BG_COLOR
)
status_label.pack(pady=5)


# ======================
# CORE (Animated)
# ======================

core_frame = tk.Frame(root, bg=BG_COLOR)
core_frame.pack(pady=10)

core_label = tk.Label(
    core_frame,
    text="⬤",
    font=("Segoe UI", 72),
    fg=ACCENT_COLOR,
    bg=BG_COLOR
)
core_label.pack()

pulse = True
current_status_color = ACCENT_COLOR


def animate_core():
    global pulse, current_status_color
    if pulse:
        core_label.config(fg=current_status_color)
    else:
        core_label.config(fg="#1a2a4a")
    pulse = not pulse
    root.after(500, animate_core)


# ======================
# DASHBOARD
# ======================

dashboard_frame = tk.Frame(root, bg=PANEL_COLOR, highlightbackground=ACCENT_COLOR, highlightthickness=1, bd=0)
dashboard_frame.pack(pady=10, padx=30, fill="x")

def make_dash_label(text, fg, default="--"):
    lbl = tk.Label(
        dashboard_frame,
        text=f"{text}: {default}",
        fg=fg,
        bg=PANEL_COLOR,
        font=("Consolas", 13, "bold")
    )
    lbl.pack(side="left", padx=25, pady=12)
    return lbl

cpu_label = make_dash_label("CPU", "#00ff9d")
ram_label = make_dash_label("RAM", "#00ffff")
battery_label = make_dash_label("BAT", "#f1c40f")
time_label = make_dash_label("TIME", ACCENT_COLOR)


# ======================
# MEMORY DASHBOARD
# ======================

memory_frame = tk.Frame(root, bg=PANEL_COLOR, highlightbackground=ACCENT_COLOR, highlightthickness=1, bd=0)
memory_frame.pack(fill="x", padx=30, pady=5)

def make_mem_label(text):
    lbl = tk.Label(
        memory_frame,
        text=f"{text}: 0",
        fg=ACCENT_COLOR,
        bg=PANEL_COLOR,
        font=("Consolas", 12, "bold")
    )
    lbl.pack(side="left", padx=20, pady=8)
    return lbl

projects_label = make_mem_label("PROJECTS")
tasks_label = make_mem_label("TASKS")
goals_label = make_mem_label("GOALS")
notes_label = make_mem_label("NOTES")
journal_label = make_mem_label("JOURNAL")


# ======================
# CHAT AREA
# ======================

terminal_label = tk.Label(
    root,
    text="SYSTEM TERMINAL",
    font=("Consolas", 11, "bold"),
    fg=ACCENT_COLOR,
    bg=BG_COLOR
)
terminal_label.pack(pady=(15, 0))

chat_box = scrolledtext.ScrolledText(
    root,
    bg="#0c1426",
    fg=TEXT_COLOR,
    font=FONT_CHAT,
    wrap="word",
    bd=0,
    insertbackground=ACCENT_COLOR,
    selectbackground=ACCENT_COLOR,
    selectforeground="#000000",
    padx=15,
    pady=15
)
chat_box.pack(fill="both", expand=True, padx=30, pady=(5, 10))

chat_box.tag_config("nova", foreground=ACCENT_COLOR, font=(FONT_CHAT[0], FONT_CHAT[1], "bold"))
chat_box.tag_config("user", foreground=SUCCESS_COLOR)
chat_box.tag_config("system", foreground=TEXT_DIM)
chat_box.config(state="disabled")


# ======================
# INPUT AREA
# ======================

input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.pack(fill="x", padx=30, pady=(0, 15))

user_input = tk.Entry(
    input_frame,
    bg=PANEL_COLOR,
    fg=TEXT_COLOR,
    insertbackground=ACCENT_COLOR,
    font=FONT_CHAT,
    bd=0,
    highlightbackground=ACCENT_COLOR,
    highlightcolor=ACCENT_COLOR,
    highlightthickness=1
)
user_input.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=8)
user_input.bind("<Return>", lambda e: send_message())


def style_button(btn, bg_color, hover_color):
    btn.configure(
        bg=bg_color,
        fg="#000000",
        activebackground=hover_color,
        activeforeground="#000000",
        font=FONT_BUTTON,
        bd=0,
        padx=20,
        pady=8,
        cursor="hand2"
    )
    def on_enter(e): btn.configure(bg=hover_color)
    def on_leave(e): btn.configure(bg=bg_color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def send_message():
    text = user_input.get().strip()
    if not text:
        return
    user_input.delete(0, tk.END)
    add_message("You", text, "user")
    process_input(text)


send_button = tk.Button(input_frame, text="SEND", command=send_message)
send_button.pack(side="right")
style_button(send_button, ACCENT_COLOR, "#33e0ff")


# ======================
# CHAT FUNCTIONS
# ======================

def add_message(sender, message, tag="nova"):
    chat_box.config(state="normal")
    prefix = {
        "NOVA": "[NOVA] ► ",
        "You": "[USER] ► ",
        "SYSTEM": "[SYSTEM] ► "
    }.get(sender, "[?] ► ")
    chat_box.insert(tk.END, f"\n{prefix}{message}\n", tag)
    chat_box.config(state="disabled")
    chat_box.see(tk.END)

    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        with open("chat_history.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {sender}: {message}\n")
    except Exception:
        pass


def process_input(text):
    set_status("thinking")
    response = ""
    try:
        for chunk in get_stream_response(text):
            response += chunk
    except Exception as exc:
        response = f"Error: {exc}"

    if response == "EXIT_NOVA":
        add_message("NOVA", "Shutting down.", "system")
        set_status("offline")
        try:
            speak("Shutting down")
        except Exception:
            pass
        root.after(0, quit_app)
        return

    add_message("NOVA", response, "nova")
    set_status("speaking")
    try:
        speak(response)
    except Exception:
        pass
    set_status("listening")


# ======================
# NOVA LOOP (Voice)
# ======================

def nova_loop():
    global nova_running
    while nova_running:
        set_status("listening")
        try:
            text = listen()
        except Exception:
            text = ""
        if not text:
            continue
        root.after(0, lambda t=text: add_message("You", t, "user"))
        set_status("thinking")
        response = ""
        try:
            for chunk in get_stream_response(text):
                response += chunk
        except Exception as exc:
            response = f"Error: {exc}"
        if response == "EXIT_NOVA":
            root.after(0, lambda: add_message("NOVA", "Shutting down.", "system"))
            set_status("offline")
            try:
                speak("Shutting down")
            except Exception:
                pass
            root.after(0, quit_app)
            break
        root.after(0, lambda r=response: add_message("NOVA", r, "nova"))
        set_status("speaking")
        try:
            speak(response)
        except Exception:
            pass
        set_status("listening")


# ======================
# START / STOP
# ======================

def start_nova():
    global nova_running
    if nova_running:
        add_message("NOVA", "Already running.", "system")
        return
    nova_running = True
    add_message("NOVA", "System activated.", "system")
    show_notification("NOVA", "System activated")
    try:
        speak("Nova is now online")
    except Exception:
        pass
    threading.Thread(target=nova_loop, daemon=True).start()


def stop_nova():
    global nova_running
    nova_running = False
    set_status("offline")
    add_message("NOVA", "System stopped.", "system")
    show_notification("NOVA", "System stopped")


# ======================
# SYSTEM TRAY
# ======================

def show_window(icon=None, item=None):
    root.after(0, root.deiconify)


def hide_window():
    root.withdraw()


def quit_app(icon=None, item=None):
    global nova_running
    nova_running = False
    try:
        if icon:
            icon.stop()
    except Exception:
        pass
    root.destroy()


def create_tray():
    try:
        image = Image.open("nova_icon.ico")
    except Exception:
        image = Image.new("RGB", (64, 64), (0, 255, 255))
    menu = pystray.Menu(
        pystray.MenuItem("Show NOVA", show_window),
        pystray.MenuItem("Start Listening", tray_start_nova),
        pystray.MenuItem("Stop Listening", tray_stop_nova),
        pystray.MenuItem("Morning Brief", tray_morning_brief),
        pystray.MenuItem("Status Report", tray_status_report),
        pystray.MenuItem("Exit", quit_app),
    )
    icon = pystray.Icon("NOVA", image, "NOVA Assistant", menu)
    icon.run()


def minimize_to_tray():
    hide_window()
    threading.Thread(target=create_tray, daemon=True).start()


def tray_start_nova(icon=None, item=None):
    root.after(0, start_nova)


def tray_stop_nova(icon=None, item=None):
    root.after(0, stop_nova)


def tray_morning_brief(icon=None, item=None):
    try:
        result = get_response("morning briefing")
    except Exception as exc:
        result = f"Error: {exc}"
    root.after(0, lambda: add_message("NOVA", result, "nova"))


def tray_status_report(icon=None, item=None):
    try:
        result = get_response("status report")
    except Exception as exc:
        result = f"Error: {exc}"
    root.after(0, lambda: add_message("NOVA", result, "nova"))


def hotkey_listen():
    add_message("NOVA", "Hotkey activated.", "system")
    set_status("listening")
    try:
        text = listen()
    except Exception:
        text = ""
    if not text:
        set_status("offline")
        return
    root.after(0, lambda t=text: add_message("You", t, "user"))
    set_status("thinking")
    try:
        response = get_response(text)
    except Exception as exc:
        response = f"Error: {exc}"
    root.after(0, lambda r=response: add_message("NOVA", r, "nova"))
    set_status("speaking")
    try:
        speak(response)
    except Exception:
        pass
    set_status("offline")


keyboard.add_hotkey(
    "ctrl+n",
    lambda: threading.Thread(target=hotkey_listen, daemon=True).start()
)


# ======================
# STATUS HELPER
# ======================

def set_status(mode):
    global current_status_color
    colors = {
        "online": ONLINE_COLOR,
        "listening": ACCENT_COLOR,
        "thinking": THINKING_COLOR,
        "speaking": SPEAKING_COLOR,
        "offline": OFFLINE_COLOR,
    }
    current_status_color = colors.get(mode, "white")
    status_label.config(text=f"● {mode.upper()}", fg=current_status_color)


# ======================
# DASHBOARD UPDATE
# ======================

def update_dashboard():
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        try:
            battery = psutil.sensors_battery()
        except Exception:
            battery = None
        battery_text = f"Battery: {battery.percent}%" if battery else "Battery: N/A"
        current_time = datetime.now().strftime("%I:%M:%S %p")

        cpu_label.config(text=f"CPU: {cpu}%")
        ram_label.config(text=f"RAM: {ram}%")
        battery_label.config(text=battery_text)
        time_label.config(text=f"Time: {current_time}")

        stats = get_stats()
        projects_label.config(text=f"PROJECTS: {stats.get('projects', 0)}")
        tasks_label.config(text=f"TASKS: {stats.get('tasks', 0)}")
        goals_label.config(text=f"GOALS: {stats.get('goals', 0)}")
        notes_label.config(text=f"NOTES: {stats.get('notes', 0)}")
        journal_label.config(text=f"JOURNAL: {stats.get('journal', 0)}")
    except Exception:
        pass
    root.after(2000, update_dashboard)


# ======================
# BUTTONS
# ======================

button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="▶ START", command=start_nova)
start_button.pack(side="left", padx=8)
style_button(start_button, SUCCESS_COLOR, "#00e87d")

stop_button = tk.Button(button_frame, text="■ STOP", command=stop_nova)
stop_button.pack(side="left", padx=8)
style_button(stop_button, OFFLINE_COLOR, "#c0392b")

tray_button = tk.Button(button_frame, text="⬇ TRAY", command=minimize_to_tray)
tray_button.pack(side="left", padx=8)
style_button(tray_button, "#34495e", "#4a6278")


# ======================
# STARTUP
# ======================

add_message("NOVA", "System initialized.", "system")
add_message("NOVA", "Ready for commands. Type in the box or press Ctrl+N for voice.", "system")

animate_core()
update_dashboard()

root.protocol("WM_DELETE_WINDOW", root.destroy)

root.mainloop()
