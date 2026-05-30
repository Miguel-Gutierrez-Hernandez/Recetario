from plyer import stt
from utils.talk import talk

def listen():
    command = ""
    try:
        print("Escuchando...")
        talk("Escuchando...")
        stt.start()           # abre el reconocedor nativo de Android
        command = stt.last_text.lower().strip()
        print(command)
    except Exception as e:
        print("Error:", e)
    return command