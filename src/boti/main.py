import speech_recognition as sr
import pyttsx3, pywhatkit, wikipedia, datetime, keyboard
from pygame import mixer
from config import NAME

listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[92].id)


def talk(text):
    engine.say(text)
    engine.runAndWait()

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

def run():
    command = listen()

    if 'reproduce' in command:
        song = command.replace('reproduce', '').strip()
        talk('Reproduciendo ' + song)
        pywhatkit.playonyt(song)

    elif 'busca' in command:
        topic = command.replace('busca', '').strip()
        wikipedia.set_lang('es')
        talk('Buscando ' + topic + ' en Wikipedia')
        info = wikipedia.summary(topic, sentences=1) # sentences=1 para obtener solo el primer párrafo, puedes ajustar este número según tus necesidades
        print(info)
        talk(info)

if __name__ == '__main__':
    run()