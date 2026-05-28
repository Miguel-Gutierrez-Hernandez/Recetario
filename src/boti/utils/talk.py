import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[92].id)


def talk(text):
    engine.say(text)
    engine.runAndWait()