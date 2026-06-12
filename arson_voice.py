import pyttsx3

def speak(text):
    engine = pyttsx3.init()  # fresh engine every call
    engine.setProperty('rate', 175)

    engine.say(text)
    engine.runAndWait()
    engine.stop()