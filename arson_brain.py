def get_response(text):
    text = text.lower()

    if "hello" in text:
        return "Hello Abir. How can I help you today?"

    elif "your name" in text:
        return "I am ARSON. Your personal AI operating companion."

    elif "how are you" in text:
        return "All systems are operational."

    elif "goodbye" in text:
        return "Goodbye Abir."

    else:
        return "I do not know the answer to that yet."