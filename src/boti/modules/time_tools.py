import datetime, re
from utils.talk import talk
from pygame import mixer


def time_now(command=None):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    talk("La hora actual es " + current_time)

def set_alarm(command):
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
