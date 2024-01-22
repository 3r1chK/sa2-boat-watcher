# SaApi.py
import requests


class SaApi:
    def __init__(self, username, key, api_url='https://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl'):
        self.username = username
        self.key = key
        self.api_url = api_url

    def fetch_data(self):
        """Calls the API and returns data of all the boats."""
        params = {'usrnr': self.username, 'key': self.key}
        response = requests.get(self.api_url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def fetch_boat_data(self, boat):
        """Calls the API and returns data of a single boat."""
        all_boat_data = self.fetch_data()
        if all_boat_data:
            # Filters data to find the correct boat
            for boat_data in all_boat_data:
                if boat_data.get('boatname') == boat.name and boat_data.get('boattype') == boat.boat_type:
                    return boat_data
        return None
