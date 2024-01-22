# SaWatcher.py
import time


class SaWatcher:
    def __init__(self, boat, api, period):
        self.boat = boat
        self.api = api
        self.period = period

    def start_monitoring(self):
        """Start monitoring cycle that executes periodical API calls."""
        try:
            while True:
                log = self.api.fetch_boat_data(self.boat)
                if log:
                    self.boat.add_log(log)
                    self.boat.save_polar_file()
                time.sleep(self.period)
        except KeyboardInterrupt:
            # Compute interpolated values
            self.boat.compute_missing_values()
            self.boat.save_polar_file()
            self.boat.polar.export_polar_file()

            print("Monitoring manually stopped.")
