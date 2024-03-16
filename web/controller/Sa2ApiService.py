from src.SaUserBoatApi import SaUserBoatApi
from web.controller.ConfigService import ConfigService
from web.model.Boat import Boat


class Sa2ApiService:

    def __init__(self):
        pass    # todo init SaApi class for the call?

    @staticmethod
    def get_boat_data(boat: Boat):
        username = ConfigService().get('username')
        api_key = ConfigService().get('api_key')
        if username is None or api_key is None:
            raise Exception('Missing configuration: username or api_key not registered in Config(s)')
        api = SaUserBoatApi(username=username, api_private_key=api_key)
        boat_data = api.fetch_boat_data_by_name(boat.name)
        if boat_data is None:
            return False
        else:
            return boat_data
