import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()
recognizer = sr.Recognizer()

while True:
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)

        print("You:", text)

        if text.lower() == "exit":
            engine.say("Goodbye Abir")
            engine.runAndWait()
            break

        from arson_brain import get_response

        response = get_response(text)
        print("ARSON:", response)

        engine.say(response)
        engine.runAndWait()

    except Exception as e:
        print("Error:", e)