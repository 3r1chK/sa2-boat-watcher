# SaWatcher.py
import time


class SaWatcher:
    def __init__(self, boat, api, period):
        self.boat = boat
        self.api = api
        self.period = period
        self.nmea_server = None

    def start_monitoring(self, nmea_server=None):
        """Start monitoring cycle that executes periodical API calls."""
        if nmea_server is not None:
            self.nmea_server = nmea_server
            self.nmea_server.start_server()
        try:
            while True:
                log = self.api.fetch_boat_data(self.boat)
                if log:
                    self.boat.add_log(log)
                    self.boat.save_polar_file()
                    if self.nmea_server is not None:
                        self.nmea_server.send_boatlog(log)
                time.sleep(self.period)
        except KeyboardInterrupt:
            # Compute interpolated values
            self.boat.compute_missing_values()
            self.boat.save_polar_file()
            self.boat.polar.export_polar_file()
            if self.nmea_server is not None:
                self.nmea_server.stop_server()

            print("Monitoring manually stopped.")
