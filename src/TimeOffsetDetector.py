# TimeOffsetDetector.py
from datetime import datetime, timedelta
from src.GribInterpolator import GribInterpolator
from pupygrib import _strip_zeros
import bz2


class TimeOffsetDetector:
    MAX_RECURSION = 8   # For grib file importation/extraction
    IS_DEBUG = 2
    max_hours_to_spread = 6
    grib_interpolation_time_steps = 15  # [minutes]
    detection_precision = 15    # [minutes]

    def __init__(self,
                 api, grib_file, hours_to_spread=None, detection_precision=None, grib_interpolation_time_steps=None
                 ):
        self.results = {}   # Dict{datetime->float} ~~ Dict{datetime->rate}
        self.api = api
        self.grib_file = self.import_grib_file(grib_file)
        self.enrich_grib_data()
        if hours_to_spread is not None:
            self.max_hours_to_spread = hours_to_spread
        if detection_precision is not None:
            self.detection_precision = detection_precision
        if grib_interpolation_time_steps is not None:
            self.grib_interpolation_time_steps = grib_interpolation_time_steps

    def launch_detector(self):
        """
        Launches the weather accuracy detector. Spreads the detection over a predefined
        time range and prints the weather accuracy rates.
        """
        raise NotImplementedError("The TimeOffsetDetector class doesn't implement the launch_detector method")

    def enrich_grib_data(self):
        """
        Enrich the grib_file data by calculating the missing value by linear interpolation between GRIB messages.
        """
        interpolator = GribInterpolator(self.grib_file, self.grib_interpolation_time_steps)
        self.grib_file = self.import_grib_file(interpolator.interpolate_twd_and_tws())

    def import_grib_file(self, grib_file, c=0):
        """
        Imports a GRIB file, handling decompression and format verification. Can be called recursively.
        """
        if c > TimeOffsetDetector.MAX_RECURSION:
            raise Exception(f"Max recursion depth exceeded ({TimeOffsetDetector.MAX_RECURSION})")

        with open(grib_file, 'rb') as stream:
            # Skip initial zeros since some GRIB files seem to be padded with
            # zeros between the messages.
            _strip_zeros(stream, 256)

            # Check that we have a GRIB message
            magic = stream.read(4)
            self.debug_print(f"GRIB file magic bytes: \"{magic}\"")

            if not magic:
                raise Exception("Trying to import a corrupetd or empty file.")
            if magic == b"BZh9":
                grib_file = self.decompress_bzGrib(grib_file)
                return self.import_grib_file(grib_file, c + 1)
            if magic != b"GRIB":
                raise Exception("Not a GRIB message")

            # TODO: remove messages out of range to radically increase performances!
            return grib_file

    def decompress_bzGrib(self, compressed_grib_file):
        """
        Decompresses a GRIB file compressed with bzip2.
        """
        decompressed_data = None
        # Open the compressed file
        with bz2.open(compressed_grib_file, 'rb') as compressed_file:
            decompressed_data = compressed_file.read()

        # Ensure that decompressed data is not None or empty
        if decompressed_data is None or len(decompressed_data) == 0:
            raise Exception("Empty (decompressed) grib file.")

        # Write the decompressed data to the output file path
        output_file_path = compressed_grib_file.replace(".", "") + "_.grib"
        with open(output_file_path, 'wb') as output_file:
            output_file.write(decompressed_data)

        # Return the path to the decompressed file
        return output_file_path

    def debug_print(self, message):
        if self.IS_DEBUG:
            print(message)

    def verbose_print(self, message):
        if self.IS_DEBUG and self.IS_DEBUG > 1:
            print(message)

    def get_datetimes_to_try(self) -> list[datetime]:
        times_to_try = []

        # Get current time and add it to the tries
        now = datetime.utcnow()
        times_to_try.append(now)

        # Calculate the minimum and maximum times
        time_spread = timedelta(hours=self.max_hours_to_spread)
        min_time = now - time_spread
        max_time = now + time_spread

        # Spread backward
        tmp_time = now
        while min_time <= tmp_time:
            tmp_time = tmp_time - timedelta(minutes=self.detection_precision)
            times_to_try.append(tmp_time)

        # Spread forward
        tmp_time = now
        while max_time >= tmp_time:
            tmp_time = tmp_time + timedelta(minutes=self.detection_precision)
            times_to_try.append(tmp_time)

        # Sort and return the resulting datetime list
        return sorted(times_to_try)

    def shift_grib_in_new_file(self, new_grib_file_path: str, time_delta: timedelta = None):
        """
        Takes the original GRIB file and shifts it in time so to meet the best rate.
        If time delta is provided, it will shift the GRIB file in time by its value.
        """
        raise NotImplementedError()
