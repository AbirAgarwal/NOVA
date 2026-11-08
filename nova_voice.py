"""
NOVA Voice System - Text-to-Speech with female voice default
"""

import pyttsx3


def speak(text: str, voice_id=None):
    """Speak text using female voice if available."""
    engine = pyttsx3.init()

    voices = engine.getProperty("voices")

    selected_voice = voice_id

    if selected_voice is None:
        # Try to find a female voice
        for v in voices:
            name = (v.name or "").lower()
            id_str = (v.id or "").lower()
            if any(k in name or k in id_str
                   for k in ["female", "zira", "hazel", "susan", "karen", "samantha", "heather", "jessica"]):
                selected_voice = v.id
                break

        # Fallback: use second voice if available (often female on Windows)
        if selected_voice is None and len(voices) > 1:
            selected_voice = voices[1].id
        # Fallback: use first available voice
        elif selected_voice is None and len(voices) > 0:
            selected_voice = voices[0].id

        if selected_voice:
            engine.setProperty("voice", selected_voice)
    else:
        engine.setProperty("voice", selected_voice)

    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()
    engine.stop()


def get_available_voices():
    """Return list of available voices for GUI selection."""
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    result = []
    if voices:
        for v in voices:
            result.append({
                "id": v.id,
                "name": v.name or "Unknown",
                "gender": "Female" if any(k in (v.name or "").lower()
                                          for k in ["female", "zira", "hazel", "susan", "karen", "samantha", "heather", "jessica"])
                else "Male/Other",
            })
    return result
