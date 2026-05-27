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
    
    elif 'hora' in command:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        talk("La hora actual es " + current_time)
    
    elif 'alarma' in command:
        alarm_time = command.replace('alarma', '').strip()

        try:
            alarm_hour, alarm_minute = map(int, alarm_time.split(':')) # Separa la hora y los minutos hay que asegurarse de que el formato sea correcto
            talk(f"Alarma configurada para las {alarm_hour:02d}:{alarm_minute:02d}.")
            print(f"Alarma configurada para las {alarm_hour:02d}:{alarm_minute:02d}.")

            while True:
                now = datetime.datetime.now()
                if now.hour == alarm_hour and now.minute == alarm_minute:
                    talk("¡Es hora de despertar!")
                    mixer.init()
                    mixer.music.load('alarm_sound.mp3')  # Asegúrate de tener un archivo de sonido llamado 'alarm_sound.mp3' en el mismo directorio
                    mixer.music.play()
                    break

        except ValueError:
            talk("Lo siento, no pude entender la hora. Por favor, asegúrate de decirla en formato de 24 horas, por ejemplo, 18:30.")
            print("Hora no válida. Por favor, intenta nuevamente.")

if __name__ == '__main__':
    run()