# TimeOffsetDetectorByLocation.py
from datetime import datetime, timedelta
import numpy as np
from src.GeoPoint import GeoPoint
from src.PyGribUtils import PyGribUtils
from src.SaGetWeatherApi import SaGetWeatherApi
from src.TimeOffsetDetector import TimeOffsetDetector


class TimeOffsetDetectorByLocation(TimeOffsetDetector):
    grib_locations_count = 4
    IS_DEBUG = 1

    def __init__(self, api: SaGetWeatherApi, grib_file, grib_locations_count=None,
                 hours_to_spread=None, detection_precision=None, grib_interpolation_time_steps=None
                 ):
        """
        Constructor for initializing the class with an API object and a GRIB file.
        """
        super().__init__(api, grib_file, hours_to_spread, detection_precision, grib_interpolation_time_steps)
        if grib_locations_count is not None:
            self.grib_locations_count = grib_locations_count
        self.locations = []     # list[GeoPoint]

    def launch_detector(self):
        """
        Launches the weather accuracy detector. Spreads the detection over a predefined
        time range and prints the weather accuracy rates.
        """
        # Find (GRIB_LOCATIONS_COUNT) useful points from the GRIB file
        self.get_locations_from_grib()
        if len(self.locations) <= 0:
            raise Exception("No locations found in the grib file")

        # Get weather accuracy in the spread times
        times_to_try = self.get_datetimes_to_try()

        # Enrich each (useful) GeoPoint with SA2 (current) weather data
        for location in self.locations:
            self.get_single_location_sa2_weather(location)

        # Get (average) accuracy rate for each time to try, and save the results
        rates = self.get_avg_accuracy_rates(times_to_try)

        # Save and print results
        self.results = rates
        self.print_results()

    def print_results(self):
        rates = self.results

        self.debug_print("@" * 64 + "\n")
        self.debug_print("TOP 5 rates:")
        i = 0
        now = datetime.utcnow()
        for key, value in reversed(sorted(rates.items(), key=lambda item: item[1])):
            i += 1
            if i > 5: break
            # Compute time difference from now
            sign = "-"
            timediff = now - key  # -> (positive) [datetime.timedelta]
            if key > now:
                timediff = key - now
                sign = "+"
            formatted_timediff = (f"{sign}{int(timediff.total_seconds() // 3600)}h "
                                  f"{int((timediff.total_seconds() // 60) % 60)}m")
            self.debug_print(f"{i}# {key} ({formatted_timediff} from now) with a rate of {value:.4f}")
        self.debug_print("\n" + "@" * 64)
        self.debug_print("\nWhole computed set:")
        i = 0
        for key in sorted(rates):
            i += 1
            self.debug_print(f"{i} {key} -> {rates[key]}")
        self.debug_print("\n" + "@" * 64)

    def get_avg_accuracy_rates(self, times_to_try):
        # Get (average) accuracy rate for each time to try, and save the results

        rates = {}
        for time_to_try in times_to_try:
            # Parse locations (get accuracy rate for each location)
            rate = 0
            last_grib_datetime = None
            for location in self.locations:
                # Compare sa2 and grib weather wind components for the current time, in the current location
                loc_rate, grib_datetime = self.get_weather_accuracy_rate_at_point_in_time(location, time_to_try)
                self.verbose_print(f"\t[{location.latitude}, {location.longitude}]"
                                   f" Weather accuracy at time {grib_datetime} is {loc_rate}.")

                # Execution smell: if last_grib_time and grib_time differs, means something is aleatory in the process
                # to choose the closest (in time) grib message (in `get_weather_accuracy_rate_at_point_in_time()`)
                if last_grib_datetime is not None and grib_datetime != last_grib_datetime:
                    print("[WARNING] The found times in GRIB file differs for the previous found "
                          "using the same original datetime!!")

                # Update external variables
                last_grib_datetime = grib_datetime
                rate += loc_rate

            # Compute the average value of the locations' rates
            rate = rate / len(self.locations)

            # Save and print the results
            rates[last_grib_datetime] = rate
            self.verbose_print(f"Weather (avg) accuracy rate at time {last_grib_datetime} is {rate}.")

        return rates

    def get_weather_accuracy_rate_at_point_in_time(self, point: GeoPoint, date_time: datetime) -> (float, datetime):
        """
        Returns the weather accuracy comparing:
         - on a side, the SA2 weather obtained by the API (for current datetime in the current point);
         - on the other, the weather values in the GRIB file (for the given date_time in the current point).
        It compares winds U and V components from the GRIB file and from SA2 server.
        :param point:
        :param date_time:
        :return:
        """
        # Compare weathers for the point location with the forecasted weather from the selected messages in that point
        sa2_u_component, sa2_v_component = point.data['environment']['windu'], point.data['environment']['windv']
        grib_u_component, grib_v_component, grib_datetime = (
            PyGribUtils.get_single_location_grib_winds(self.grib_file, point.latitude, point.longitude, date_time))

        u_component_error = (sa2_u_component - grib_u_component) ** 2
        v_component_error = (sa2_v_component - grib_v_component) ** 2
        rmse = np.sqrt((u_component_error + v_component_error) / 2)

        return 1 / rmse if rmse != 0 else 1, grib_datetime

    def get_single_location_sa2_weather(self, point: GeoPoint):
        """
        Gets the weather from the SA2 api for each location and add the result to the GeoPoint
        """
        self.api.update_params(new_params={'lat': point.latitude, 'lon': point.longitude})
        point.update_data(self.api.fetch_data(False))

    def get_locations_from_grib(self):
        min_lat, max_lat, min_lon, max_lon = PyGribUtils.get_grib_extremes(self.grib_file)
        # TODO: spread over the diagonal to find other GRIB points (use GRIB_LOCATIONS_COUNT)
        points = [GeoPoint(max_lat, max_lon), GeoPoint(min_lat, min_lon), GeoPoint(max_lat, min_lon),
                  GeoPoint(min_lat, max_lon)]   # #4
        self.locations = points[:(self.grib_locations_count % 5)]

    def shift_grib_in_new_file(self, new_grib_file_path: str = "/tmp/generated_grib.grb", time_delta: timedelta = None):
        """
        Takes the original GRIB file and shifts it in time so to meet the best rate.
        If time delta is provided, it will shift the GRIB file in time by its value.
        """
        # If no time_delta is provided, let's compute it by the difference between the best rate and now
        if time_delta is None:
            if self.results is None or len(self.results) == 0:
                raise Exception("No results found, so I can't get best rate to shift the grib file in time.")
            # We want to move the GRIB file from datetime_with_highest_rate to now, so we need to know how far it is
            # (time_delta)
            now = datetime.utcnow()
            datetime_with_highest_rate = max(self.results.keys(), key=lambda k: self.results[k])
            time_delta = now - datetime_with_highest_rate

        self.debug_print(f"Creating new GRIB file shifted by {int(time_delta.total_seconds()/3600)} hours "
                         f"and {int((time_delta.total_seconds()/60) % 60)} minutes "
                         f"(file saved @ '{new_grib_file_path}').")
        PyGribUtils.shift_grib_file_in_time(self.grib_file, new_grib_file_path, time_delta=time_delta)
