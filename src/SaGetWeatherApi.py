# SaGetWeatherApi.py
from src.SaApi import SaApi


class SaGetWeatherApi(SaApi):
    REQUIRED_PARAMS = ['lat', 'lon']

    def __init__(self, latitude, longitude, api_url='https://backend.sailaway.world/cgi-bin/sailaway/getenvironment.pl'):
        super().__init__(api_url=api_url, params={'lat': latitude, 'lon': longitude})
