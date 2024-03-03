# PyGribTimeOffsetDetectorByBoat.py
from src.PyGribUtils import PyGribUtils
from src.TimeOffsetDetectorByBoat import TimeOffsetDetectorByBoat
import pygrib
import numpy as np
from datetime import datetime

from src.Utils import Utils


class PyGribTimeOffsetDetectorByBoat(TimeOffsetDetectorByBoat):

    def __init__(self, api, grib_file):
        super().__init__(api, grib_file)

    def location_in_grib(self, boat_data) -> bool:
        latitude, longitude = boat_data.get('latitude'), boat_data.get('longitude')
        min_lat, max_lat, min_lon, max_lon = PyGribUtils.get_grib_extremes(self.grib_file)
        res = min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon
        if self.IS_DEBUG:
            boat_name, latm, latM, lonm, lonM = boat_data.get('boatname'), min_lat, max_lat, min_lon, max_lon
            if not res:
                self.debug_print(f"[x] \"{boat_name}\" is not in ({latm}, {lonm}), ({latM}, {lonM}), but at {latitude}, {longitude}")
            else:
                self.debug_print(f"[v] \"{boat_name}\" is in ({latm}, {lonm}), ({latM}, {lonM}), at {latitude}, {longitude}")
        return res

    def get_boat_weather_accuracy_rate(self, boat_data, timestamp) -> (float, datetime, float, float, float):
        # Generates a weather accuracy rate valuating the SA2 weather from boat_data and the grib message
        # closest in time to the given timestamp
        closest_u_wind_msg, closest_v_wind_msg, dt = (PyGribUtils.get_closest_wind_grib_messages_in_time
                                                      (self.grib_file, timestamp))

        # Ensure we have both U and V components
        if closest_u_wind_msg is None or closest_v_wind_msg is None:
            return 0  # Or handle this case differently?

        # Get messages locations
        u_lats, u_lons = closest_u_wind_msg.latlons()
        v_lats, v_lons = closest_v_wind_msg.latlons()

        # Ensure that locations coincide - then also the values' indexes
        if not np.array_equal(u_lats, v_lats) or not np.array_equal(u_lons,v_lons):
            raise Exception("Exception occurred during calculation of weather accuracy rate: lat-lon not coincide")

        # Get boat location
        boat_lat = boat_data['latitude']
        boat_lon = boat_data['longitude']

        def find_nearest_grib_values_index(message, target_lat, target_lon):
            lats, lons = message.latlons()
            # Compute the absolute difference array
            abs_diff_lat = np.abs(lats - target_lat)
            abs_diff_lon = np.abs(lons - target_lon)
            # Find the index of the smallest difference
            return np.unravel_index(np.argmin(abs_diff_lat + abs_diff_lon), lats.shape)

        # Get the U and V data
        u_wind_data = closest_u_wind_msg.values
        v_wind_data = closest_v_wind_msg.values

        # Find the index of the nearest point to the boat's location
        u_index = find_nearest_grib_values_index(closest_u_wind_msg, boat_lat, boat_lon)
        v_index = find_nearest_grib_values_index(closest_v_wind_msg, boat_lat, boat_lon)
        if u_index != v_index:
            self.debug_print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                             "Something weird happening with values indexes!")

        # Get the U and V components for the nearest point
        closest_u_wind = u_wind_data[u_index]
        closest_v_wind = v_wind_data[u_index]

        # Calculate TWS (wind speed)
        tws = np.sqrt(closest_u_wind ** 2 + closest_v_wind ** 2)

        # Calculate TWD (wind direction)
        twd = (np.arctan2(closest_v_wind, closest_u_wind) * 180 / np.pi) % 360

        # Calculate the accuracy rate using the boat's TWD and TWS
        actual_twd = boat_data['twd']
        actual_tws = boat_data['tws']

        twd_error = (twd - actual_twd) ** 2
        tws_error = (tws - actual_tws) ** 2
        rmse = np.sqrt((twd_error + tws_error) / 2)

        self.debug_print(f"\tBoat: %s" % (boat_data.get('boatname')))
        self.debug_print(f"\t\tGrib TWD vs boat TWD (error): {twd} vs {actual_twd} ({twd_error})")
        self.debug_print(f"\t\tGrib TWS vs boat TWS (error): {tws} vs {actual_tws} ({tws_error})")
        self.debug_print(f"\t\tRMSE: {rmse} (%f)" % (1 / rmse if rmse != 0 else 1))

        if self.IS_DEBUG and False:
            print('Twd error: ', twd_error)
            print('Tws error: ', tws_error)
            print('RMSE: ', rmse)
            if rmse != 0:
                print("1/rmse: ", 1/rmse)

        return (
            1 / rmse if rmse != 0 else 1,
            Utils.datetime_from_validity_date_and_time(closest_u_wind_msg.validityDate, closest_u_wind_msg.validityTime),
            rmse,
            twd_error,
            tws_error
        )

    def get_boat_weather_accuracy_rate2(self, boat_data, timestamp) -> float:
        with pygrib.open(self.grib_file) as grb:
            closest_twd = None
            closest_tws = None
            min_time_diff = float('inf')

            for msg in grb:
                msg_time = msg.analDate
                time_diff = abs((msg_time - timestamp).total_seconds())

                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    lats, lons = msg.latlons()
                    idx = np.argmin((lats - boat_data['latitude']) ** 2 + (lons - boat_data['longitude']) ** 2)

                    if 'twd' in msg.keys() and 'tws' in msg.keys():
                        closest_twd = msg['twd'].values.flat[idx]
                        closest_tws = msg['tws'].values.flat[idx]

            if closest_twd is None or closest_tws is None:
                return 0  # Or handle this case differently

            actual_twd = boat_data['twd']
            actual_tws = boat_data['tws']
            twd_error = (closest_twd - actual_twd) ** 2
            tws_error = (closest_tws - actual_tws) ** 2
            rmse = np.sqrt((twd_error + tws_error) / 2)

            return 1 / rmse if rmse != 0 else float('inf')
