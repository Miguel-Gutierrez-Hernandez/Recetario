import speech_recognition as sr
import pyttsx3, pywhatkit, wikipedia, datetime, keyboard, re
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
    command = "alarma 0:36"

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
    
    elif 'hora' in command:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        talk("La hora actual es " + current_time)
    
    elif 'alarma' in command:
        # Extract HH:MM pattern directly from the command
        match = re.search(r'\b(\d{1,2}:\d{2})\b', command)

        if match:
            alarm_time = datetime.datetime.strptime(match.group(1), "%H:%M").strftime("%H:%M")
            try:
                talk(f"Alarma configurada para las {alarm_time}.")
                print(f"Alarma configurada para las {alarm_time}.")

                while True:
                    if datetime.datetime.now().strftime("%H:%M") == alarm_time:
                        talk("¡Es hora de despertar!")
                        print("¡Es hora de despertar!")
                        mixer.init()
                        mixer.music.load('alarma.mp3')
                        mixer.music.play()
                        while mixer.music.get_busy():
                            input("Pulsa ENTER para detener la alarma")
                            mixer.music.stop()
                        break

            except ValueError:
                talk("Lo siento, no pude entender la hora.")
        else:
            talk("No encontré una hora válida. Di por ejemplo: alarma a las 14:30.")
            print("No se encontró hora en el comando.")


if __name__ == '__main__':
    run()