# Utils.py
from datetime import datetime


class Utils:
    KNOTS_FOR_METERS = 1.94384

    @staticmethod
    def meters_to_knots(m):
        return m*Utils.KNOTS_FOR_METERS

    @staticmethod
    def degree_sum(a, b):
        return (a + b) % 360

    @staticmethod
    def get_current_datetime_formatted():
        # Get the current datetime
        current_datetime = datetime.utcnow()
        # Format the datetime in "YYYYMMDD_HHmmss" format
        formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
        return formatted_datetime

    @staticmethod
    def datetime_from_validity_date_and_time(validity_date: int, validity_time: int) -> datetime:
        # 0 = MIDNIGHT of yesterday
        # 1 = 0100
        if type(validity_time) is int:
            validity_time = str(validity_time)
            if len(validity_time) < 4:
                missing_zeroes = 4 - len(validity_time)
                validity_time = "0"*missing_zeroes + validity_time
        if type(validity_date) is int:
            validity_date = str(validity_date)

        # Ensure the strings are in the correct format
        if len(validity_date) != 8 or len(validity_time) != 4:
            raise TypeError("Date or time format is incorrect")

        year = int(validity_date[:4])
        month = int(validity_date[4:6])
        day = int(validity_date[6:])
        hour = int(validity_time[:2])
        minute = int(validity_time[2:])

        # Construct and return the datetime object
        return datetime(year, month, day, hour, minute)

    @staticmethod
    def dictionary_has_all_keys(dictionary: dict, keys_list: list) -> bool:
        """
        Checks if all values of the list are present (as keys) in the dictionary.

        :param dictionary: Dictionary in which to check for keys from the list.
        :param keys_list: The list of keys to check.
        :return: True if all keys from keys_list are in dictionary, False otherwise.
        """
        return all(key in dictionary for key in keys_list)
