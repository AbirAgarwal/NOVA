from listen import listen
from arson_brain import get_response
from arson_voice import speak
from automation import run_command

print("ARSON ONLINE")
speak("ARSON is now online")

while True:
    text = listen()

    if not text:
        continue

    if text.lower() in ["exit", "quit", "stop"]:
        speak("Goodbye Abir")
        break

    command_response = run_command(text)

    if command_response:
        print("ARSON:", command_response)
        speak(command_response)
        continue

    response = get_response(text)

    print("ARSON:", response)
    speak(response)