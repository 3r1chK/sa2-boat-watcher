# main.py
import configparser
from src.NmeaServer import NmeaServer
from src.SaWatcher import SaWatcher
from src.SaApi import SaApi
from src.Boat import Boat


def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config


def main():
    config = load_config("conf.ini")

    boat = Boat(config['Boat']['name'], config['Boat']['type'], config['Boat']['polar_file'])
    api = SaApi(config['General']['username'], config['General']['key'], str(config['General']['url']))
    watcher = SaWatcher(boat, api, int(config['General']['period']))

    if config['NmeaServer']['enabled']:
        watcher.start_monitoring(NmeaServer(config['NmeaServer']['host'], int(config['NmeaServer']['port'])))
    else:
        watcher.start_monitoring()


if __name__ == "__main__":
    main()
