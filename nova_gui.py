import threading
import tkinter as tk
import psutil
from datetime import datetime
from nova_voice import speak
from listen import listen
from nova_brain import get_response
from memory_manager import get_stats,show_notification
import pystray
from PIL import Image
import keyboard
import gui_controller



# ======================
# WINDOW
# ======================
root = tk.Tk()

gui_controller.GUI_ROOT = root
root.iconbitmap("nova_icon.ico")
root.title("NOVA")
root.geometry("1200x800")
root.configure(bg="#0a0f1f")

nova_running = False

# ======================

# TITLE

# ======================

title = tk.Label(
    root,
    text="◉ NOVA CORE",
    font=("Segoe UI", 30, "bold"),
    fg="#00ffff",
    bg="#0a0f1f"
)

title.pack(pady=10)

version_label = tk.Label(
root,
text="v1.4",
font=("Arial", 10),
fg="gray",
bg="#0a0f1f"
)

version_label.pack()

# ======================

# STATUS

# ======================

status_label = tk.Label(
root,
text="Status: Online",
font=("Segoe UI", 11),
fg="white",
bg="#0a0f1f"
)

status_label.pack(pady=5)

# =====================

# CORE

# ======================

core_label = tk.Label(
    root,
    text="⬤",
    font=("Segoe UI",60),
    fg="#00ffff",
    bg="#0a0f1f"
)

core_label.pack()
pulse = True
current_status_color = "#00ffff"

def animate_core():

    global pulse

    if pulse:
        core_label.config(
            fg=current_status_color
        )
    else:
        core_label.config(
            fg="#203050"
        )

    pulse = not pulse

    root.after(
        600,
        animate_core
    )

# ======================

# DASHBOARD

# ======================

dashboard_frame = tk.Frame(
    root,
    bg="#121826",
    highlightbackground="#00ffff",
    highlightthickness=1
)

dashboard_frame.pack(pady=10)

cpu_label = tk.Label(
dashboard_frame,
text="CPU: --%",
fg="lightgreen",
bg="#0a0f1f"
)

cpu_label.pack(
side="left",
padx=20
)

ram_label = tk.Label(
dashboard_frame,
text="RAM: --%",
fg="lightgreen",
bg="#0a0f1f"
)

ram_label.pack(
side="left",
padx=20
)

battery_label = tk.Label(
dashboard_frame,
text="Battery: --%",
fg="lightgreen",
bg="#0a0f1f"
)

battery_label.pack(
side="left",
padx=20
)

time_label = tk.Label(
dashboard_frame,
text="Time: --:--",
fg="lightgreen",
bg="#0a0f1f"
)

time_label.pack(
side="left",
padx=20
)

# ======================
# MEMORY DASHBOARD
# ======================

memory_frame = tk.Frame(
    root,
    bg="#121826",
    highlightbackground="#00ffff",
    highlightthickness=1
)

memory_frame.pack(
    fill="x",
    padx=20,
    pady=5
)

projects_label = tk.Label(
    memory_frame,
    text="Projects: 0",
    fg="cyan",
    bg="#111111"
)

projects_label.pack(
    side="left",
    padx=15
)

tasks_label = tk.Label(
    memory_frame,
    text="Tasks: 0",
    fg="cyan",
    bg="#111111"
)

tasks_label.pack(
    side="left",
    padx=15
)

goals_label = tk.Label(
    memory_frame,
    text="Goals: 0",
    fg="cyan",
    bg="#111111"
)

goals_label.pack(
    side="left",
    padx=15
)

notes_label = tk.Label(
    memory_frame,
    text="Notes: 0",
    fg="cyan",
    bg="#111111"
)

notes_label.pack(
    side="left",
    padx=15
)

journal_label = tk.Label(
    memory_frame,
    text="Journal: 0",
    fg="cyan",
    bg="#111111"
)

journal_label.pack(
    side="left",
    padx=15
)

terminal_label = tk.Label(
    root,
    text="SYSTEM TERMINAL",
    font=("Consolas",10,"bold"),
    fg="#00ffff",
    bg="#0a0f1f"
)

terminal_label.pack()

# ======================

# QUICK ACTIONS

# ======================

quick_frame = tk.Frame(
root,
bg="#0a0f1f"
)

quick_frame.pack(pady=5)

tk.Button(
quick_frame,
    text="Briefing",
    command=lambda:
    add_message(
        "NOVA",
        get_response(
            "morning briefing"
        )
    )
).pack(side="left", padx=5)

tk.Button(
    quick_frame,
    text="Status",
    command=lambda:
    add_message(
        "NOVA",
        get_response(
            "status report"
        )
    )
).pack(side="left", padx=5)

tk.Button(
    quick_frame,
    text="Projects",
    command=lambda:
    add_message(
        "NOVA",
        get_response(
            "list projects"
        )
    )
).pack(side="left", padx=5)

tk.Button(
    quick_frame,
    text="Tasks",
    command=lambda:
    add_message(
        "NOVA",
        get_response(
            "show tasks"
        )
    )
).pack(side="left", padx=5)

# ======================

# CHAT FUNCTIONS

# ======================

def add_message(sender, message):


    chat_box.config(
        state="normal"
    )

    if sender == "NOVA":

        chat_box.insert(
            tk.END,
            f"\n[NOVA] ► {message}\n",
            "nova"
        )

    else:

        chat_box.insert(
            tk.END,
            f"\n[USER] ► {message}\n",
            "user"
        )

    chat_box.config(
        state="disabled"
    )

    chat_box.see(tk.END)

    timestamp = datetime.now().strftime(
        "%H:%M:%S"
    )

    with open(
        "chat_history.txt",
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"[{timestamp}] {sender}: {message}\n"
        )


# ======================

# NOVA LOOP

# ======================

def nova_loop():

    global nova_running

    while nova_running:

        set_status("listening")

        text = listen()

        if not text:
            continue

        add_message(
            "You",
            text
        )

        set_status("thinking")

        response = get_response(text)

        # Voice Exit
        if response == "EXIT_NOVA":

            add_message(
                "NOVA",
                "Shutting down."
            )

            set_status("offline")

            speak(
                "Shutting down"
            )

            root.after(
                0,
                quit_app
            )

            break

        add_message(
            "NOVA",
            response
        )

        set_status("speaking")

        speak(response)

        set_status("listening")


# ======================

# START / STOP

# ======================

def start_nova():


    global nova_running

    if nova_running:

        add_message(
            "NOVA",
            "Already running."
        )

        return

    nova_running = True

    add_message(
        "NOVA",
        "System activated."
    )
    show_notification(
        "NOVA",
        "System activated"
    )
    speak(
        "Nova is now online"
    )

    threading.Thread(
        target=nova_loop,
        daemon=True
    ).start()


def stop_nova():

    global nova_running

    nova_running = False

    set_status("offline")

    add_message(
        "NOVA",
        "System stopped."
    )
    show_notification(
        "NOVA",
        "System stopped"
    )

def show_window(icon=None, item=None):

    root.after(
        0,
        root.deiconify
    )


def hide_window():

    root.withdraw()


def quit_app(icon=None, item=None):

    global nova_running

    nova_running = False

    if icon:
        icon.stop()

    root.destroy()

def create_tray():
    print("Creating tray icon...")
    image = Image.open("nova_icon.ico")

    menu = pystray.Menu(

        pystray.MenuItem(
            "Show NOVA",
            show_window
        ),

        pystray.MenuItem(
            "Start Listening",
            tray_start_nova
        ),

        pystray.MenuItem(
            "Stop Listening",
            tray_stop_nova
        ),

        pystray.MenuItem(
            "Morning Brief",
            tray_morning_brief
        ),

        pystray.MenuItem(
            "Status Report",
            tray_status_report
        ),

        pystray.MenuItem(
            "Exit",
            quit_app
        )
    )
    
    icon = pystray.Icon(
        "NOVA",
        image,
        "NOVA Assistant",
        menu
    )

    icon.run()

def minimize_to_tray():
    print("Minimizing to tray...S")
    hide_window()

    threading.Thread(
        target=create_tray,
        daemon=True
    ).start()

def tray_start_nova(icon=None, item=None):

    root.after(
        0,
        start_nova
    )


def tray_stop_nova(icon=None, item=None):

    root.after(
        0,
        stop_nova
    )


def tray_morning_brief(icon=None, item=None):

    result = get_response(
        "morning briefing"
    )

    root.after(
        0,
        lambda: add_message(
            "NOVA",
            result
        )
    )


def tray_status_report(icon=None, item=None):

    result = get_response(
        "status report"
    )

    root.after(
        0,
        lambda: add_message(
            "NOVA",
            result
        )
    )

def hotkey_listen():

    add_message(
        "NOVA",
        "Hotkey activated."
    )

    status_label.config(
        text="Status: Listening 🎤"
    )

    text = listen()

    if not text:
        return

    add_message(
        "You",
        text
    )

    status_label.config(
        text="Status: Thinking 🧠"
    )

    response = get_response(text)

    add_message(
        "NOVA",
        response
    )

    status_label.config(
        text="Status: Speaking 🔊"
    )

    speak(response)

    status_label.config(
        text="Status: Ready"
    )

keyboard.add_hotkey(
    "ctrl+n",
    lambda: threading.Thread(
        target=hotkey_listen,
        daemon=True
    ).start()
)

current_status_color = "#00ffff"

def set_status(mode):

    global current_status_color

    colors = {
        "online":"#00ff9d",
        "listening":"#00ffff",
        "thinking":"#f1c40f",
        "speaking":"#9b59b6",
        "offline":"#e74c3c"
    }

    current_status_color = colors.get(
        mode,
        "white"
    )

    status_label.config(
        text=f"● {mode.upper()}",
        fg=current_status_color
    )

# ======================
# DASHBOARD UPDATE
# ======================

def update_dashboard():

    cpu = psutil.cpu_percent()

    ram = psutil.virtual_memory().percent

    try:
        battery = psutil.sensors_battery()
    except:
        battery = None

    if battery:

        battery_text = (
            f"Battery: {battery.percent}%"
        )

    else:

        battery_text = "Battery: N/A"

    current_time = datetime.now().strftime(
        "%I:%M:%S %p"
    )

    cpu_label.config(
        text=f"CPU: {cpu}%"
    )

    ram_label.config(
        text=f"RAM: {ram}%"
    )

    battery_label.config(
        text=battery_text
    )

    time_label.config(
        text=f"Time: {current_time}"
    )

    stats = get_stats()

    projects_label.config(
        text=f"Projects: {stats['projects']}"
    )

    tasks_label.config(
        text=f"Tasks: {stats['tasks']}"
    )

    goals_label.config(
        text=f"Goals: {stats['goals']}"
    )

    notes_label.config(
        text=f"Notes: {stats['notes']}"
    )

    journal_label.config(
        text=f"Journal: {stats['journal']}"
    )

    root.after(
        2000,
        update_dashboard
    )

# ======================
# BUTTONS
# ======================

button_frame = tk.Frame(
    root,
    bg="#0a0f1f"
)

button_frame.pack(pady=10)


start_button = tk.Button(
    button_frame,
    text="▶ START",
    command=start_nova,
    bg="#00b894",
    fg="white",
    font=("Segoe UI",10,"bold"),
    bd=0,
    padx=20,
    pady=8
)

start_button.pack(side="left", padx=10)

stop_button = tk.Button(
    button_frame,
    text="■ STOP",
    command=stop_nova,
    bg="#e74c3c",
    fg="white",
    font=("Segoe UI",10,"bold"),
    bd=0,
    padx=20,
    pady=8
)

stop_button.pack(side="left", padx=10)

tray_button = tk.Button(
    button_frame,
    text="⬇ TRAY",
    command=minimize_to_tray,
    bg="#34495e",
    fg="white",
    font=("Segoe UI",10,"bold"),
    bd=0,
    padx=20,
    pady=8
)

tray_button.pack(side="left", padx=10)

# ======================

# CHAT AREA

# ======================

chat_box = tk.Text(
    root,
    bg="#121826",
    fg="white",
    font=("Segoe UI", 11),
    wrap="word",
    bd=0,
    insertbackground="white"
)

chat_box.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(5,20)
    )

chat_box.tag_config(
"nova",
foreground="cyan"
)

chat_box.tag_config(
"user",
foreground="lightgreen"
)

chat_box.config(
state="disabled"
)


# ======================
# STARTUP
# ======================

add_message(
"NOVA",
"System initialized."
)

add_message(
"NOVA",
"Ready for commands."
)

animate_core()

update_dashboard()

root.protocol(
    "WM_DELETE_WINDOW",
    root.destroy
)
print("Before mainloop")


root.mainloop()

