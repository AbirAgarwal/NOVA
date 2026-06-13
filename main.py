from listen import listen
from nova_brain import get_response
from nova_voice import speak
from automation import run_command
from ai_brain import get_ai_response
print("NOVA ONLINE")
speak("NOVA is now online")

while True:
    text = listen()

    if not text:
        continue

    text = text.lower()
    
    if not text.startswith("nova"):
        continue

    text = text.replace("nova", "", 1).strip() 

    if text.lower() in ["exit", "quit", "stop", "shutdown"]:
        speak("Goodbye Abir")
        break

    command_response = run_command(text)

    if command_response:
        print("NOVA:", command_response)
        speak(command_response)
        continue

    response = get_response(text)

    if response == "I am still learning.":
        response = get_ai_response(text)

    print("NOVA:", response)
    speak(response)