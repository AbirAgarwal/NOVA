import threading
import tkinter as tk
from nova_voice import speak
from listen import listen
from nova_brain import get_response
from datetime import datetime

root = tk.Tk()

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

# Status
status_label = tk.Label(
    root,
    text="Status: Online",
    font=("Arial", 12),
    fg="white",
    bg="black"
)
status_label.pack()

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

    while True:

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

    status_label.config(text="Status: Listening 🎤")

    add_message("NOVA", "System activated.")

    speak("Nova is now online")

    threading.Thread(
        target=nova_loop,
        daemon=True
    ).start()


def stop_nova():
    status_label.config(text="Status: Offline")
    chat_box.insert(tk.END, "\nNOVA stopped.\n")


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

root.mainloop()
