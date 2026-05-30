import datetime, re
from plyer import audio, tts
from utils.talk import talk

def time_now(command=None):
    current_time = datetime.datetime.now().strftime("%H:%M")
    talk("La hora actual es " + current_time)

def set_alarm(command=None):
    match = re.search(r'\b(\d{1,2}:\d{2})\b', command)
    if match:
        alarm_time = datetime.datetime.strptime(match.group(1), "%H:%M").strftime("%H:%M")
        talk(f"Alarma configurada para las {alarm_time}.")
        while True:
            if datetime.datetime.now().strftime("%H:%M") == alarm_time:
                talk("¡Es hora de despertar!")
                audio.play('alarma.mp3')
                input("Pulsa ENTER para detener")
                audio.stop()
                break
    else:
        talk("No encontré una hora válida.")