# SaUserBoatApi.py
from src.Boat import Boat
from src.SaApi import SaApi


class SaUserBoatApi(SaApi):
    REQUIRED_PARAMS = ['key', 'usrnr']

    def __init__(self, username, api_private_key, api_url='https://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl'):
        super().__init__(api_private_key, api_url, params={'usrnr': username})

    def fetch_boat_data(self, boat: Boat):
        """Calls the API and returns data of a single boat."""
        all_boat_data = self.fetch_data()
        if all_boat_data:
            if all_boat_data.error is not None:
                raise Exception("Error fetching boat data: {}".format(all_boat_data))
            # Filters data to find the correct boat
            for boat_data in all_boat_data:
                if boat_data.get('boatname') == boat.name and boat_data.get('boattype') == boat.boat_type:
                    return boat_data
        return None

    def fetch_boat_data_by_name(self, boat_name: str):
        """Calls the API and returns data of a single boat."""
        all_boat_data = self.fetch_data()
        if all_boat_data:
            # Filters data to find the correct boat
            for boat_data in all_boat_data:
                if boat_data.get('boatname') == boat_name:
                    return boat_data
        return None
