from utils.keywords import COMMANDS
from utils.talk import talk
from utils.listener import listen

def run():
    command = listen()
    for keyword, func in COMMANDS.items():
        if keyword in command:
            func(command)
            break
        else:
            talk("No entendí el comando.")
            print("Comando no reconocido:", command)
    

if __name__ == '__main__':
    run()