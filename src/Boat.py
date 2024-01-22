# Boat.py
from src.BoatPolar import BoatPolar
from src.BoatLog import BoatLog


class Boat:
    def __init__(self, name, boat_type, polar_file):
        self.name = name
        self.boat_type = boat_type
        self.polar = BoatPolar(name, boat_type, polar_file)
        self.logs = []

    def add_log(self, log_data):
        # Crea un nuovo BoatLog
        new_log = BoatLog(log_data)

        # Aggiungi il log all'elenco dei log della barca
        self.logs.append(new_log)

        # Aggiorna il BoatPolar con il nuovo log
        self.polar.update_from_log(new_log)

    def save_polar_file(self):
        # Salva i dati aggiornati del polar file
        self.polar.save_to_file()

    def compute_missing_values(self):
        self.polar.interpolate_twa()
