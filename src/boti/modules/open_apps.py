import subprocess as sp
import os
from config import PROGRAMS, SEARCH_ENGINES, FILE_PATH
from utils.talk import talk

def open_apps(command):
    opened = False

    for name, url in SEARCH_ENGINES.items():
        if name in command:
            talk("Abriendo: " + name)
            print("Abriendo: " + name)
            sp.call(["open", url.format(command.replace('abre', '').strip())])
            opened = True
            break

    if not opened:
        for name, path in PROGRAMS.items():
            if name in command:
                talk("Abriendo: " + name)
                print("Abriendo: " + name)
                sp.call(["open", "-a", path])
                opened = True
                break

    if not opened:
        talk("No reconocí ningún programa ni navegador.")
        print("Comando no reconocido.")

def open_file(command):
    for name, path in FILE_PATH.items():
        if name in command:
            # Resolve path relative to this script file, not the working directory
            abs_path = os.path.join(os.path.dirname(__file__), path)
            if os.path.exists(abs_path):
                talk("Abriendo archivo: " + name)
                print("Abriendo archivo: " + name)
                sp.call(["open", abs_path])  # macOS native open
            else:
                talk(f"No encontré el archivo {name}.")
                print(f"Ruta no encontrada: {abs_path}")
            break
    else:
        talk("No se reconoció ningún archivo.")