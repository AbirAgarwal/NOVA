import os
import webbrowser
import psutil
from urllib.parse import quote
from datetime import datetime

def run_command(text):
    text = text.lower()

    if "open chrome" in text:
        os.system("start chrome")
        return "Opening Chrome."

    elif "open vscode" in text or "open visual studio code" in text:
        os.system("code")
        return "Opening Visual Studio Code."

    elif "open youtube" in text:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    elif "open github" in text:
        webbrowser.open("https://github.com")
        return "Opening GitHub."
    
    elif "open calculator" in text:
        os.system("calc")
        return "Opening Calculator."
    
    elif "open notepad" in text:
        os.system("notepad")
        return "Opening Notepad."
    
    elif "open downloads" in text:
        os.startfile(os.path.join(os.path.expanduser("~"), "Downloads"))
        return "Opening Downloads."

    elif "open documents" in text:
        os.startfile(os.path.join(os.path.expanduser("~"), "Documents"))
        return "Opening Documents."

    elif "open desktop" in text:
        os.startfile(os.path.join(os.path.expanduser("~"), "Desktop"))
        return "Opening Desktop."

    elif "open file explorer" in text:
        os.system("explorer")
        return "Opening File Explorer."
    
    elif "search google for" in text:
        query = text.replace("search google for", "").strip()

        if query:
            webbrowser.open(
                f"https://www.google.com/search?q={quote(query)}"
        )
            return f"Searching Google for {query}"
    
    elif "search youtube for" in text:
        query = text.replace("search youtube for", "").strip()

        if query:
            webbrowser.open(
                f"https://www.youtube.com/results?search_query={quote(query)}"
        )
            return f"Searching YouTube for {query}"
    

    elif "what time" in text:
        return f"The time is {datetime.now().strftime('%I:%M %p')}"

    elif "date" in text:
        return f"Today is {datetime.now().strftime('%B %d, %Y')}"
    
    elif "battery status" in text:
        battery = psutil.sensors_battery()

        if battery:
            percent = battery.percent
            plugged = battery.power_plugged

            if plugged:
                return f"Battery is at {percent} percent and charging."

            return f"Battery is at {percent} percent."
    
        return "I could not detect the battery."
    
    elif "system info" in text:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent

        return f"CPU usage is {cpu} percent. Memory usage is {ram} percent."
    
    return None