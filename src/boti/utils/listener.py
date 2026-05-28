import speech_recognition as sr
from utils.talk import talk
from config import NAME

listener = sr.Recognizer()

def listen():
    command = ""

    try:
        with sr.Microphone() as source:
            print("Escuchando...")
            talk("Escuchando...")
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