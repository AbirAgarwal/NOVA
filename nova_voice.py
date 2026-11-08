import pyttsx3


def speak(text):
    engine = pyttsx3.init()

    voices = engine.getProperty("voices")

    # Safe voice selection — fall back to first available voice
    if voices and len(voices) > 2:
        engine.setProperty("voice", voices[2].id)
    elif voices:
        engine.setProperty("voice", voices[0].id)

    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()
    engine.stop()
