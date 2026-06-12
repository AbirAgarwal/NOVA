import os
import webbrowser


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

    return None