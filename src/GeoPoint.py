# GeoPoint.py


class GeoPoint(object):
    def __init__(self, latitude, longitude, data=None):
        self.latitude = latitude
        self.longitude = longitude
        self.data = data

    def update_data(self, new_data):
        self.data = new_data

    def get_data(self):
        return self.data
