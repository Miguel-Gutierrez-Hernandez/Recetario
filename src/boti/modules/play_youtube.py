from utils.talk import talk
import pywhatkit

def play_youtube(command):
    song = command.replace('reproduce', '').strip()
    talk('Reproduciendo ' + song)
    pywhatkit.playonyt(song)
