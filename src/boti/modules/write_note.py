import os
from utils.write import write
from config import PATH_FILE

def write_note(command=None):
    file_note = os.path.join(os.path.dirname(__file__), PATH_FILE['nota'])
    try:
        with open(file_note, 'a') as file:
            write(file)
    except FileNotFoundError:
        file = open(file_note, 'w')
        write(file)