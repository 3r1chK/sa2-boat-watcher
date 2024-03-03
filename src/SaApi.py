# SaApi.py
import requests
from src.Utils import Utils
from src.execution_time_monitor import execution_time_monitor


class SaApi:
    REQUIRED_PARAMS = ['']

    def __init__(self, api_private_key=None, api_url='https://srv.sailaway.world/cgi-bin/sailaway/', params=None):
        if params is None:
            params = {}
        self.api_url = api_url
        self.params = params
        if api_private_key is not None:
            self.params['key'] = api_private_key

    def verify_params(self, params=None):
        if ((params is None and not Utils.dictionary_has_all_keys(self.params, self.REQUIRED_PARAMS))
                or (params is not None and not Utils.dictionary_has_all_keys(params, self.REQUIRED_PARAMS))):
            raise Exception(f"Trying to call {self.api_url} with wrong parameters (required are {self.REQUIRED_PARAMS})")

    def update_params(self, new_params=None):
        if new_params is None:
            new_params = {}
        # Check if the 'key' key is present in the original parameters; if so, and it's not present in the new_params,
        # copy it from the original parameters!
        if 'key' in self.params and self.params['key'] is not None:
            if 'key' not in new_params or new_params['key'] is None:
                new_params['key'] = self.params['key']
        # Verify required parameters exist
        try:
            self.verify_params(new_params)
        except Exception as e:
            print("Exception occurred trying to update SaApi parameters: check passed parameters and try again")
            return
        # Update the params
        self.params = new_params

    @execution_time_monitor
    def fetch_data(self, mocked=False):
        """Calls the API endpoint and returns data."""
        if mocked:
            import json

            with open('tmp/example.json') as f:
                d = json.load(f)
                return d
        else:
            params = self.params
            response = requests.get(self.api_url, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception('The API returned an error code: ' + str(response.status_code))
