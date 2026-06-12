from listen import listen
from arson_brain import get_response
from arson_voice import speak
from automation import run_command
from ai_brain import get_ai_response
print("ARSON ONLINE")
speak("ARSON is now online")

while True:
    text = listen()

    if not text:
        continue

    text = text.lower()
    
    if not text.startswith("arson"):
        continue

    text = text.replace("arson", "", 1).strip() 

    if text.lower() in ["exit", "quit", "stop"]:
        speak("Goodbye Abir")
        break

    command_response = run_command(text)

    if command_response:
        print("ARSON:", command_response)
        speak(command_response)
        continue

    response = get_response(text)

    if response == "I am still learning.":
        response = get_ai_response(text)

    print("ARSON:", response)
    speak(response)