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

# ======================

# WINDOW

# ======================

root = tk.Tk()

root.title("NOVA")
root.geometry("1000x650")
root.configure(bg="black")

nova_running = False

# ======================

# TITLE

# ======================

title = tk.Label(
root,
text="NOVA",
font=("Arial", 28, "bold"),
fg="cyan",
bg="black"
)

title.pack(pady=10)

version_label = tk.Label(
root,
text="v1.4",
font=("Arial", 10),
fg="gray",
bg="black"
)

version_label.pack()

# ======================

# STATUS

# ======================

status_label = tk.Label(
root,
text="Status: Online",
font=("Arial", 12),
fg="white",
bg="black"
)

status_label.pack(pady=5)

# ======================

# DASHBOARD

# ======================

dashboard_frame = tk.Frame(
root,
bg="black"
)

dashboard_frame.pack(pady=10)

cpu_label = tk.Label(
dashboard_frame,
text="CPU: --%",
fg="lightgreen",
bg="black"
)

cpu_label.pack(
side="left",
padx=20
)

ram_label = tk.Label(
dashboard_frame,
text="RAM: --%",
fg="lightgreen",
bg="black"
)

ram_label.pack(
side="left",
padx=20
)

battery_label = tk.Label(
dashboard_frame,
text="Battery: --%",
fg="lightgreen",
bg="black"
)

battery_label.pack(
side="left",
padx=20
)

time_label = tk.Label(
dashboard_frame,
text="Time: --:--",
fg="lightgreen",
bg="black"
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
    bg="#111111",
    bd=2,
    relief="ridge"
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

# ======================

# QUICK ACTIONS

# ======================

quick_frame = tk.Frame(
root,
bg="black"
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

main_frame = tk.Frame(
    root,
    bg="black"
)

main_frame.pack(
    fill="both",
    expand=True
)

# ======================

# CHAT AREA

# ======================

chat_box = tk.Text(
root,
bg="#111111",
fg="white",
font=("Consolas", 12),
wrap="word"
)

chat_box.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
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

# CHAT FUNCTIONS

# ======================

def add_message(sender, message):


    chat_box.config(
        state="normal"
    )

    if sender == "NOVA":

        chat_box.insert(
            tk.END,
            f"\n🤖 NOVA: {message}\n",
            "nova"
        )

    else:

        chat_box.insert(
            tk.END,
            f"\n🧑 You: {message}\n",
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


    while nova_running:

        status_label.config(
            text="Status: Listening 🎤"
        )

        text = listen()

        if not text:
            continue

        add_message(
            "You",
            text
        )

        status_label.config(
            text="Status: Thinking 🧠"
        )

        response = get_response(
            text
        )

        add_message(
            "NOVA",
            response
        )

        status_label.config(
            text="Status: Speaking 🔊"
        )

        speak(response)

        status_label.config(
            text="Status: Listening 🎤"
        )


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

    status_label.config(
        text="Status: Offline"
    )

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
    image = Image.new(
        "RGB",
        (64, 64),
        color="cyan"
    )

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
    "space",
    lambda: threading.Thread(
        target=hotkey_listen,
        daemon=True
    ).start()
)

# ======================
# DASHBOARD UPDATE
# ======================

def update_dashboard():

    cpu = psutil.cpu_percent()

    ram = psutil.virtual_memory().percent

    battery = psutil.sensors_battery()

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
bg="black"
)

button_frame.pack(pady=10)

start_button = tk.Button(
button_frame,
text="Start",
command=start_nova
)

start_button.pack(
side="left",
padx=10
)

stop_button = tk.Button(
button_frame,
text="Stop",
command=stop_nova
)

stop_button.pack(
side="left",
padx=10
)

tray_button = tk.Button(
    button_frame,
    text="Hide To Tray",
    command=minimize_to_tray
)

tray_button.pack(
    side="left",
    padx=10
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

update_dashboard()

root.protocol(
    "WM_DELETE_WINDOW",
    root.destroy
)

root.mainloop()

