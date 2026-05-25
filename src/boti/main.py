import speech_recognition as sr
import pyttsx3
import pywhatkit
from config import NAME

listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def talk(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    command = ""

    try:
        with sr.Microphone() as source:
            print("Escuchando...")
            audio = listener.listen(source)

            command = listener.recognize_google(
                audio,
                language="es-ES"
            )

            command = command.lower()

            if NAME in command:
                command = command.replace(NAME, "")
                command = command.strip()

            print(command)

    except Exception as e:
        print("Error:", e)

    return command

def run():
    command = listen()

    if not command:
        return

    if 'reproduce' in command:
        song = command.replace('reproduce', '').strip()

        talk('Reproduciendo ' + song)

        pywhatkit.playonyt(song)

if __name__ == '__main__':
    run()