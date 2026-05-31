import datetime, re, os
from plyer import audio
from utils.talk import talk

def time_now(command=None):
    current_time = datetime.datetime.now().strftime("%H:%M")
    talk("La hora actual es " + current_time)

def set_alarm(command=None):
    match = re.search(r'\b(\d{1,2}:\d{2})\b', command)
    if match:
        alarm_time = datetime.datetime.strptime(match.group(1), "%H:%M").strftime("%H:%M")
        talk(f"Alarma configurada para las {alarm_time}.")
        alarm_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'alarma.mp3')

        while True:
            if datetime.datetime.now().strftime("%H:%M") == alarm_time:
                talk("¡Es hora de despertar!")
                audio.play(alarm_file)
                input("Pulsa ENTER para detener")
                audio.stop()
                break
    else:
        talk("No encontré una hora válida.")