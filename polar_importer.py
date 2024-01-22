import configparser
from src.Boat import Boat


def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config


if __name__ == "__main__":
    config = load_config("conf.ini")

    # Load the boat and its polar
    boat = Boat(config['Boat']['name'], config['Boat']['type'], config['Boat']['polar_file'])

    # Replace values with those took from the outside
    boat.polar.load_custom_file('polars/Polar_240120_1444.pol', delimiter=";")

    boat.save_polar_file()
