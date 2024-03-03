# TimeOffsetDetectorByBoat.py
from src.SaUserBoatApi import SaUserBoatApi
from src.TimeOffsetDetector import TimeOffsetDetector
from datetime import datetime, timedelta


class TimeOffsetDetectorByBoat(TimeOffsetDetector):
    """
    This class is designed for detecting time offsets in weather data.
    It processes GRIB (Gridded Binary) files, which are commonly used
    in meteorology to store historical and forecast weather data.
    The class provides functionality to import GRIB files, decompress them if necessary,
    and calculate weather accuracy rates based on boat data.

    Attributes:
        MAX_HOURS_TO_SPREAD: A class-level constant defining the maximum time spread for accuracy calculations (default: 6 hours).
        MAX_RECURSION: A class-level constant indicating the maximum recursion depth for file import functions (default: 8).
        api: An instance attribute that holds the API object.
        grib_file: A string representing the path to the GRIB file.
        all_boats_data: Data fetched from the API about boats.
    """

    def __init__(self, api: SaUserBoatApi, grib_file):
        """
        Constructor for initializing the class with an API object and a GRIB file.
        """
        super().__init__(api, grib_file)
        self.all_boats_data = self.api.fetch_data(False) #(mocked=TimeOffsetDetector.IS_DEBUG)
        self.filter_boats_by_location()
        self.debug_print(f"Found %i boat to compare." % (len(self.all_boats_data)))

    def launch_detector(self):
        """
        Launches the weather accuracy detector. Spreads the detection over a predefined
        time range and prints the weather accuracy rates.
        """
        # Starting from now, and spreading forward and backward in the time by 15 minutes
        # (without exceeding the MAX_HOURS_TO_SPREAD limit),
        # print all the weather accuracy rates in a well-formatted way, so that can be quickly compared
        now = datetime.utcnow()
        time_spread = timedelta(hours=TimeOffsetDetectorByBoat.max_hours_to_spread)

        # Calculate the start and end times
        start_time = now - time_spread
        end_time = now + time_spread

        # Iterate over the time range in 15-minute intervals
        current_time = start_time
        best_grib_time = None
        best_current_time = None
        best_accuracy = 0
        while current_time <= end_time:
            try:
                # Calculate the weather accuracy rate for the current time
                accuracy_rate, time_used = self.get_weather_accuracy_rate(current_time)
                if best_grib_time is None or accuracy_rate > best_accuracy:
                    best_grib_time = time_used
                    best_current_time = current_time
                    best_accuracy = accuracy_rate
                self.debug_print(f"Time: {current_time}, Weather Accuracy Rate: {accuracy_rate:.4f}")

            except Exception as e:
                print(f"Error for time {current_time}: {e}")
                if self.IS_DEBUG:
                    raise e

            # Move to the next 15-minute interval
            current_time += timedelta(minutes=TimeOffsetDetectorByBoat.detection_precision)

        self.debug_print("################################################################")
        self.debug_print(f"Best GRIB time is {best_grib_time} (local (approximation) used is {best_current_time}),"
                         f" with accuracy value of {best_accuracy}.")
        self.debug_print("################################################################")

    def get_weather_accuracy_rate(self, timestamp):
        """
        Calculates the weather accuracy rate for a given timestamp based on all available boats
        data and GRIB file contents.
        """
        if not self.all_boats_data:
            raise Exception("No boat data available.")
        # Parse each returned boat
        total_boat_weather_acc_rate = 0
        considered_boats_count = 0
        grib_time = None
        for boat_data in self.all_boats_data:
            # Get the current weather accuracy rate for the boat
            boat_weather_acc_rate, grib_time, _, _, _ = self.get_boat_weather_accuracy_rate(boat_data, timestamp)
            total_boat_weather_acc_rate += boat_weather_acc_rate
            considered_boats_count += 1
        if considered_boats_count == 0:
            raise Exception("No boat data available in this (grib) area")
        a_string = timestamp.strftime("%Y%m%d-%H%M")
        b_string = grib_time.strftime("%Y%m%d-%H%M")
        acc_ratio = total_boat_weather_acc_rate/considered_boats_count
        self.debug_print(f"Accuracy with TEST timestamp {a_string}, at grib time {b_string} is {acc_ratio} (considering {considered_boats_count} boats)")
        return total_boat_weather_acc_rate / considered_boats_count, grib_time

    def location_in_grib(self, boat_data) -> bool:
        """
        Determines if a given latitude and longitude are within the bounds of the GRIB file's data.
        """
        raise NotImplemented("TimeOffsetDetector.location_in_grib(latitude,longitude): method not implemented.")

    def get_boat_weather_accuracy_rate(self, boat_data, timestamp) -> (float, datetime, float, float, float):
        """
        Generates a weather accuracy rate valuating the SA2 weather from boat_data and the grib message
        closest in time to the given timestamp
        """
        raise NotImplemented("TimeOffsetDetector.get_boat_weather_accuracy_rate(boat_data, timestamp):"
                             " method not implemented.")

    def filter_boats_by_location(self):
        resulting_list = []
        for boat_data in self.all_boats_data:
            # Consider boats located inside our Area Of Interest (the one of the grib file)
            if self.location_in_grib(boat_data):
                resulting_list.append(boat_data)
        if len(resulting_list) == 0:
            raise Exception("No boats available in the gribs location at this moment.")
        self.all_boats_data = resulting_list
