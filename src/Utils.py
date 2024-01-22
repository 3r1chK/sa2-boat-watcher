# Utils.py


class Utils:

    KNOTS_FOR_METERS = 1.94384

    @staticmethod
    def meters_to_knots(m):
        return m*Utils.KNOTS_FOR_METERS
