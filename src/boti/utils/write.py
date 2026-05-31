from utils.talk import talk
from utils.listener import listen
import os

def write(file):
    talk("¿Qué quieres escribir?")
    print("¿Qué quieres escribir?")
    content = listen()
    file.write(content + os.linesep)  # Escribe el contenido seguido de un salto de línea
    file.flush()  # Asegura que el contenido se escriba en el archivo inmediatamente
    file.close()
    talk("Texto guardado.")
    print("Texto guardado.")