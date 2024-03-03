# PyGribUtils.py
from datetime import datetime, timedelta

import numpy as np
import pygrib
import juliandate as jd

from src.Utils import Utils
from src.execution_time_monitor import execution_time_monitor


class PyGribUtils:

    @staticmethod
    def update_grib_validity_time(grib_message, new_datetime):
        grib_message.julianDay = jd.from_gregorian(new_datetime.year, new_datetime.month, new_datetime.day,
                                                   new_datetime.hour, new_datetime.minute, new_datetime.second)
        grib_message.startStep = 0
        grib_message.stepRange = '0'
        grib_message.endStep = 0
        pygrib.reload(grib_message)     # To ensure validity Date and Time are updated
        return grib_message

    @staticmethod
    def get_grib_extremes(grib_file) -> (float, float, float, float):
        """
        Reads the grib file and returns the extreme latitudes and longitudes.
        :param grib_file:
        :return: A tuple where the elements are (ordered): minimum latitude, maximum latitude, minimum longitude,
                 maximum longitude
        """
        with pygrib.open(grib_file) as msgs:
            # Let's look at the very first message, assuming it has the same grib points of all the others
            msg = msgs.read(1)[0]
            min_lat, max_lat = (
                min(msg.latitudeOfFirstGridPointInDegrees, msg.latitudeOfLastGridPointInDegrees),
                max(msg.latitudeOfFirstGridPointInDegrees, msg.latitudeOfLastGridPointInDegrees))
            min_lon, max_lon = (
                min(msg.longitudeOfFirstGridPointInDegrees, msg.longitudeOfLastGridPointInDegrees),
                max(msg.longitudeOfFirstGridPointInDegrees, msg.longitudeOfLastGridPointInDegrees))
            return min_lat, max_lat, min_lon, max_lon

    @staticmethod
    @execution_time_monitor
    def get_single_location_grib_winds(grib_file: str, latitude: float, longitude: float, date_time: datetime) \
            -> (float, float, datetime):
        """
        Looks at the GRIB file to retrieve the wind U and V components at the given point for the given date_time
        """
        # Get the closest (in time) wind components messages from the grib file
        closest_u_wind_msg, closest_v_wind_msg, grib_datetime = (
            PyGribUtils.get_closest_wind_grib_messages_in_time(grib_file, date_time))

        # Get the closest (in space) wind components values from the selected messages
        closest_u_wind_val = PyGribUtils.get_closest_wind_value_in_space_from_grib_message(closest_u_wind_msg, latitude, longitude)
        closest_v_wind_val = PyGribUtils.get_closest_wind_value_in_space_from_grib_message(closest_v_wind_msg, latitude, longitude)

        return closest_u_wind_val, closest_v_wind_val, grib_datetime

    @staticmethod
    @execution_time_monitor
    def get_closest_wind_value_in_space_from_grib_message\
                    (grib_message: pygrib.gribmessage, latitude: float, longitude: float) -> float:
        """
        Returns the closest value from a grib message to the given latitude and longitude
        :param grib_message:
        :param latitude:
        :param longitude:
        :return:
        """
        def find_nearest_grib_values_index(message, target_lat, target_lon):
            lats, lons = message.latlons()
            # Compute the absolute difference array
            abs_diff_lat = np.abs(lats - target_lat)
            abs_diff_lon = np.abs(lons - target_lon)
            # Find the index of the smallest difference
            return np.unravel_index(np.argmin(abs_diff_lat + abs_diff_lon), lats.shape)

        # Find the index of the nearest point to the boat's location
        u_index = find_nearest_grib_values_index(grib_message, latitude, longitude)

        # Return the message value for the selected index
        return grib_message.values[u_index]

    @staticmethod
    @execution_time_monitor
    def get_closest_wind_grib_messages_in_time(grib_file: str, date_time: datetime) \
            -> (pygrib.gribmessage, pygrib.gribmessage, datetime):
        """
        Finds the grib message closest in time to the given timestamp   FIXME bottleneck !!! (maybe reducing grib fsze)
        :param grib_file:   Grib file path
        :param date_time:   Datetime to look for
        :return:    The closest U and V wind components messages in the grib file to the provided date_time and the
        used GRIB time
        """
        with pygrib.open(grib_file) as grb:
            # Initialize variables to track the closest messages in time
            closest_u_wind_msg = None
            closest_v_wind_msg = None
            u_min_time_diff = float('inf')
            v_min_time_diff = float('inf')

            # Iterate over all messages to find the closest in time
            for msg in grb:
                # Calculate the time difference
                msg_validity_datetime = Utils.datetime_from_validity_date_and_time(msg.validityDate, msg.validityTime)
                time_diff = abs(msg_validity_datetime.timestamp() - date_time.timestamp())

                # Update the closest messages if this one is closer in time
                if msg.name == '10 metre U wind component' and time_diff < u_min_time_diff:
                    u_min_time_diff = time_diff
                    closest_u_wind_msg = msg
                elif msg.name == '10 metre V wind component' and time_diff < v_min_time_diff:
                    v_min_time_diff = time_diff
                    closest_v_wind_msg = msg

            # Ensure we have both U and V components
            if closest_u_wind_msg is None or closest_v_wind_msg is None:
                raise Exception(f'Unable to find grib messages close to {date_time} from grib file "{grib_file}"')

            # Adjust the date with grib "precision steps"
            message_datetime = pygrib.julian_to_datetime(closest_u_wind_msg.julianDay)
            if closest_u_wind_msg.startStep == closest_u_wind_msg.endStep and closest_u_wind_msg.startStep > 0:
                if closest_u_wind_msg.fcstimeunits == 'hrs':
                    message_datetime += timedelta(hours=closest_u_wind_msg.startStep)

            return closest_u_wind_msg, closest_v_wind_msg, message_datetime

    @staticmethod
    @execution_time_monitor
    def shift_grib_file_in_time(grib_input_file: str, grib_output_file: str, time_delta: timedelta) -> str:
        """
        Given a source grib_input, this method takes all its messages, shifts the grib messages according to the
        time delta and save the output to the path described in the grib_output_file.
        :param grib_input_file: The input grib file to be shifted in time
        :param grib_output_file:    The output grib file to save (shifted) results
        :param time_delta:  The time delta to be used to shift the grib messages
        :return: The path to the shifted grib file
        """
        # Write data to the output file path
        with open(grib_output_file, 'wb') as output_file:
            # Parse each message from the input file
            with pygrib.open(grib_input_file) as grbs:
                for msg in grbs:
                    # Get the actual msg datetime
                    msg_datetime = pygrib.julian_to_datetime(msg.julianDay)
                    if msg.startStep == msg.endStep and msg.startStep > 0 and msg.fcstimeunits == 'hrs':
                        msg_datetime += timedelta(hours=msg.startStep)
                    # Compute the new msg datetime and update the msg itself
                    new_msg_datetime = msg_datetime + time_delta
                    PyGribUtils.update_grib_validity_time(msg, new_msg_datetime)
                    # Save the message to the new GRIB file
                    output_file.write(msg.tostring())
        return grib_output_file
