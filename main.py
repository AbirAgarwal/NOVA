from listen import listen
from nova_brain import get_response
from nova_voice import speak

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

    if text in ["exit", "quit", "stop", "shutdown"]:
        speak("Goodbye Abir")
        break

    response = get_response(text)

    print("NOVA:", response)

    speak(response)