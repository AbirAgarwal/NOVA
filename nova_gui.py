import threading
import tkinter as tk
import psutil
from datetime import datetime
from nova_voice import speak
from listen import listen
from nova_brain import get_response

root = tk.Tk()
nova_running = False
root.title("NOVA")
root.geometry("900x600")
root.configure(bg="black")

# Title
title = tk.Label(
    root,
    text="NOVA",
    font=("Arial", 28, "bold"),
    fg="cyan",
    bg="black"
)
title.pack(pady=10)

#Version
version_label = tk.Label(
    root,
    text="v1.2",
    font=("Arial",10),
    fg="gray",
    bg="black"
)
version_label.pack()

# Status
status_label = tk.Label(
    root,
    text="Status: Online",
    font=("Arial", 12),
    fg="white",
    bg="black"
)
status_label.pack()

cpu_label = tk.Label(
    root,
    text="CPU: --%",
    fg="lightgreen",
    bg="black"
)
cpu_label.pack()

ram_label = tk.Label(
    root,
    text="RAM: --%",
    fg="lightgreen",
    bg="black"
)
ram_label.pack()

battery_label = tk.Label(
    root,
    text="Battery: --%",
    fg="lightgreen",
    bg="black"
)
battery_label.pack()

time_label = tk.Label(
    root,
    text="Time: --:--",
    fg="lightgreen",
    bg="black"
)
time_label.pack()

# Chat Area
chat_box = tk.Text(
    root,
    bg="#111111",
    fg="white",
    font=("Consolas", 12)
)
chat_box.pack(fill="both", expand=True, padx=20, pady=20)

chat_box.insert(tk.END, "NOVA: System initialized.\n")


# Functions
def add_message(sender, message):

    chat_box.insert(tk.END, f"{sender}: {message}\n")
    chat_box.see(tk.END)

    timestamp = datetime.now().strftime("%H:%M:%S")

    with open("chat_history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {sender}: {message}\n")

def nova_loop():

    while nova_running:

        status_label.config(text="Status: Listening 🎤")

        text = listen()

        if not text:
            continue

        add_message("You", text)

        status_label.config(text="Status: Thinking 🧠")

        response = get_response(text)

        add_message("NOVA", response)

        status_label.config(text="Status: Speaking 🔊")

        speak(response)

        status_label.config(text="Status: Listening 🎤")

def start_nova():
    global nova_running
    
    if nova_running:
        add_message("NOVA", "Already running.")
        return
    
    nova_running = True
    
    status_label.config(text="Status: Listening 🎤")

    add_message("NOVA", "System activated.")

    speak("Nova is now online")

    threading.Thread(
        target=nova_loop,
        daemon=True
    ).start()

def update_dashboard():

    cpu = psutil.cpu_percent()

    ram = psutil.virtual_memory().percent

    battery = psutil.sensors_battery()

    if battery:
        battery_text = f"Battery: {battery.percent}%"
    else:
        battery_text = "Battery: N/A"

    current_time = datetime.now().strftime("%I:%M:%S %p")

    cpu_label.config(text=f"CPU: {cpu}%")
    ram_label.config(text=f"RAM: {ram}%")
    battery_label.config(text=battery_text)
    time_label.config(text=f"Time: {current_time}")

    root.after(2000, update_dashboard)

def stop_nova():
    global nova_running

    nova_running = False

    status_label.config(text="Status: Offline")
    
    add_message("NOVA", "System stopped.")


# Buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=10)

start_button = tk.Button(
    button_frame,
    text="Start",
    command=start_nova
)
start_button.pack(side="left", padx=10)

stop_button = tk.Button(
    button_frame,
    text="Stop",
    command=stop_nova
)
stop_button.pack(side="left", padx=10)

update_dashboard()
root.mainloop()
