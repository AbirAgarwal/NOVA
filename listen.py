import speech_recognition as sr

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True

def listen():
    with sr.Microphone() as source:
        print("Listening...")

        # faster calibration (IMPORTANT)
        recognizer.adjust_for_ambient_noise(source, duration=0.3)

        try:
            audio = recognizer.listen(
                source,
                timeout=None,
                phrase_time_limit=4
            )
        except:
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print("You:", text)
        return text
    except:
        return ""