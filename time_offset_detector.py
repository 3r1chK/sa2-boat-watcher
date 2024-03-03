# time_offset_detector.py
import configparser
from src.PyGribTimeOffsetDetectorByBoat import PyGribTimeOffsetDetectorByBoat
from src.SaGetWeatherApi import SaGetWeatherApi
from src.SaUserBoatApi import SaUserBoatApi
from src.TimeOffsetDetector import TimeOffsetDetector
from src.TimeOffsetDetectorByLocation import TimeOffsetDetectorByLocation
from src.execution_time_monitor import execution_time_monitor


def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config


def by_boat_detector(config):
    api = SaUserBoatApi(config['General']['username'], config['General']['key'], str(config['General']['url']))
    detector = PyGribTimeOffsetDetectorByBoat(api, 'gribs/20240227_161250_.grb')
    detector.launch_detector()


@execution_time_monitor
def by_location_detector(config):
    api = SaGetWeatherApi(0, 0)
    # detector = TimeOffsetDetectorByLocation(api, 'gribs/20240229_091650_.grb', hours_to_spread=6)
    detector = TimeOffsetDetectorByLocation(api, 'gribs/20240229_165728_.grb', hours_to_spread=6)
    # detector = TimeOffsetDetectorByLocation(api, 'gribs/20240229_092856_.grb', hours_to_spread=1)
    detector.launch_detector()
    detector.shift_grib_in_new_file()


def main():
    config = load_config("conf.ini")
    # by_boat_detector(config)
    by_location_detector(config)


if __name__ == "__main__":
    main()
