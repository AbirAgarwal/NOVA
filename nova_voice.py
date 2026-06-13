import pyttsx3

def speak(text):
    engine = pyttsx3.init()

    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[2].id)

    engine.setProperty("rate", 175)

    engine.say(text)
    engine.runAndWait()
    engine.stop()