# --------- IMPORTS -----------------------------------------------------------------
from modules.play_youtube import play_youtube
from modules.search_wikipedia import search_wikipedia
from modules.time_tools import time_now, set_alarm
from modules.open_apps import open_apps, open_file
from modules.write_note import write_note

# --------- COMMANDS ----------------------------------------------------------------
COMMANDS = {
    "reproduce": play_youtube,
    "busca": search_wikipedia,
    "hora": time_now,
    "alarma": set_alarm,
    "abre": open_apps,
    "archivo": open_file
}