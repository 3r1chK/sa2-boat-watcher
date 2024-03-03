# GribInterpolator.py
from datetime import timedelta
import numpy
import pygrib
import os

from src.PyGribUtils import PyGribUtils
from src.Utils import Utils


class GribInterpolator:
    OUTPUT_DIR_PATH = "/tmp/sa-watcher"

    def __init__(self, input_filepath, time_step=30):
        self.output_filepath = None
        self.input_filepath = input_filepath
        self.time_step = time_step

    def interpolate_twd_and_tws(self):
        # Main method to handle the workflow
        u_grib_messages, v_grib_messages = self.parse_grib_file()
        new_u_grib_messages, new_v_grib_messages = self.interpolate_multiple_wind_components(u_grib_messages, v_grib_messages)
        self.output_filepath = self.create_new_grib_file(new_u_grib_messages + new_v_grib_messages)
        return self.output_filepath

    def parse_grib_file(self):
        # Use pygrib to parse the input GRIB file and extract (and return) U and V components
        with pygrib.open(self.input_filepath) as grb:
            return grb.select(name='10 metre U wind component'), grb.select(name='10 metre V wind component')

    def interpolate_multiple_wind_components(self, u_grib_messages, v_grib_messages):
        # Parse the messages and add interpolated messages in between of them
        # (built to work on two messages' names)
        return self.interpolate_data(u_grib_messages), self.interpolate_data(v_grib_messages)

    def interpolate_data(self, grib_messages):
        # Parse the messages and add interpolated messages in between of them
        # (assumes every message has the same name)
        resulting_grib_messages = [grib_messages[0]]
        for i in range(1, len(grib_messages)):
            previous_message = grib_messages[i - 1]
            current_message = grib_messages[i]
            new_messages = self.interpolate_wind(previous_message, current_message)
            resulting_grib_messages += new_messages + [current_message]
        return resulting_grib_messages

    def interpolate_wind(self, start_message, end_message) -> list:
        """
        :param start_message: the starting message
        :param end_message: the ending message
        :return:
        """
        interpolated_grib_messages = []

        # Verify time difference
        start_message_datetime = Utils.datetime_from_validity_date_and_time(
            start_message.validityDate, start_message.validityTime
        )
        end_message_datetime = Utils.datetime_from_validity_date_and_time(
            end_message.validityDate, end_message.validityTime
        )
        if end_message_datetime <= start_message_datetime:
            raise Exception("Something went wrong with interpolating data: unordered grib messages received")

        # Compute interpolation steps
        time_delta = end_message_datetime - start_message_datetime
        interpolation_steps = int(time_delta.total_seconds() / (self.time_step * 60))

        # Get messages data
        start_message_values, start_message_lats, start_message_lons = start_message.data()
        end_message_values, end_message_lats, end_message_lons = end_message.data()

        # Verify values are correctly placed in space
        if (
                not numpy.array_equal(start_message_lats, end_message_lats)
                or not numpy.array_equal(start_message_lons, end_message_lons)
        ):
            return interpolated_grib_messages
            # todo raise Exception("Trying to interpolate over gribs with different locations values")

        # Compute interpolation values
        if interpolation_steps > 0:
            for step_index in range(1, interpolation_steps):   # Skip interpolation_steps+1 cause would be the last message
                fraction = step_index / interpolation_steps
                interpolation_datetime = start_message_datetime + timedelta(minutes=self.time_step)*step_index

                # Linear interpolation
                interp_message_values = start_message_values + (end_message_values - start_message_values) * fraction
                interpolated_grib_messages.append(
                    GribInterpolator
                    .create_new_grib_message(start_message, interpolation_datetime, interp_message_values)
                )

        return interpolated_grib_messages

    def create_new_grib_file(self, grib_messages):
        """
        Create a new GRIB file from a list of GRIB messages.

        :param grib_messages: List of GRIB message objects.
        """
        output_filepath = GribInterpolator.OUTPUT_DIR_PATH + os.path.basename(self.input_filepath)
        with open(output_filepath, 'wb') as file:
            for message in grib_messages:
                msg = message.tostring()  # Get the binary string of the GRIB message
                file.write(msg)
        return output_filepath

    def get_enriched_file(self):
        if self.output_filepath is None:
            raise Exception("No output file to return")
        return self.output_filepath

    @staticmethod
    def create_new_grib_message(original_message, new_datetime, new_values):
        # Create new GRIB messages with interpolated values and other values (lat,lon) from one of the original messages
        new_message = pygrib.fromstring(original_message.tostring())
        new_message["values"] = new_values
        return PyGribUtils.update_grib_validity_time(new_message, new_datetime)
