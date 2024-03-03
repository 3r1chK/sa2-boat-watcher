# BoatPolar.py
import csv
import os
from time import time
from src.Utils import Utils


class BoatPolar:
    MAX_BLIND_INTERPOLATION_DISTANCE = 10

    def __init__(self, boat_name, boat_type, polar_file):
        self.boat_name = boat_name
        self.boat_type = boat_type
        self.polar_file = polar_file
        self.polar_grid = self.initialize_polar_grid()
        # Load file from filesystem (if exists)
        self.load_file()

    @staticmethod
    def initialize_polar_grid():
        # Initialize a 181x81 grid (TWA x TWS) with all the STW set to 0
        return [[0 for _ in range(81)] for _ in range(181)]

    def update_from_log(self, log):
        return self.add_data(log.tws, log.twa, log.spd)

    def add_data(self, tws, twa, boat_speed):
        # Converts speed in knots (rounded at 2nd decimal digit)
        boat_speed = round(Utils.meters_to_knots(boat_speed), 2)
        tws = round(Utils.meters_to_knots(tws), 2)

        # Round TWS and TWA to their closer integer values
        tws = round(tws)
        twa = round(twa)

        # Ensure that TWS and TWA are within bounds (0-80 for TWS and 0-180 for TWA)
        twa = abs(twa)
        if tws < 0 or tws > 80 or twa < 0 or twa > 180:
            print("# ["+self.boat_name+"] TWS: "+str(tws)+"; TWA: "+str(twa)+"; STW: "+str(boat_speed)+"." +
                  "\n\t! Invalid input: tws must be between 0 and 80, twa must be between -180 and 180 !")
            return
        tws = min(max(tws, 0), 80)
        twa = min(max(twa, 0), 180)
        print("# ["+self.boat_name+"] TWS: "+str(tws)+"; TWA: "+str(twa)+"; STW: "+str(boat_speed)+".")

        # Update the grid only if the new boat_speed is higher than the existing one
        if boat_speed > self.polar_grid[twa][tws]:
            tmp = self.polar_grid[twa][tws]
            self.polar_grid[twa][tws] = boat_speed
            print("--> Updated, previously STW was "+str(tmp))

    def load_file(self):
        return self.load_custom_file(self.polar_file)

    def load_custom_file(self, polar_file_path, delimiter=','):
        if os.path.exists(polar_file_path):
            with open(polar_file_path, 'r') as file:
                reader = csv.reader(file, delimiter=delimiter)
                header = next(reader)[1:]  # Store (and jump) header of columns (TWS)

                # Assuming the first column of each row indicates the TWA
                for row in reader:
                    twa = int(row[0])  # Reads the TWA index of the first column
                    if 0 <= twa <= 180:
                        col_counter = 0
                        for tws in header:
                            tws = int(tws)
                            col_counter += 1
                            if 0 <= tws <= 80:
                                self.polar_grid[twa][tws] = float(row[col_counter])

    def save_to_original_file(self):
        self.save_to_new_file(new_filename=self.polar_file)

    def save_to_original_file_with_suffix(self, suffix: str):
        self.save_to_new_file(new_filename=self.polar_file + "_" + suffix + ".pol")

    def save_to_new_file(self, new_filename: str):
        with open(new_filename, 'w', newline='') as file:    # TODO newline?
            writer = csv.writer(file)
            writer.writerow(["TWA/TWS"] + [i for i in range(81)])  # Writes TWS header
            for twa, speeds in enumerate(self.polar_grid):
                writer.writerow([twa] + speeds)  # Writes TWA and speeds

    def interpolate_twa(self):
        for tws in range(81):  # For each TWS column
            # 1. Linear interpolation for external gaps
            last_known_twa = None
            for twa in range(181):  # For each TWA row
                stw = self.polar_grid[twa][tws]
                if stw > 0:
                    if last_known_twa is not None and abs(last_known_twa-twa) > 1:
                        # Linear interpolation between last_known_twa and twa
                        self.linear_interpolation(tws, last_known_twa, twa)
                    last_known_twa = twa

            # 2. Values extension toward extremes
            if last_known_twa is not None:
                # Toward TWA=0
                self.extend_to_extremes(tws, last_known_twa, False)
                # Toward TWA=180
                self.extend_to_extremes(tws, last_known_twa, True)

    def linear_interpolation(self, tws, start_twa, end_twa):
        start_stw = self.polar_grid[start_twa][tws]
        end_stw = self.polar_grid[end_twa][tws]
        delta = (end_stw - start_stw) / (end_twa - start_twa)
        for twa in range(start_twa + 1, end_twa):
            interpolated_stw = start_stw + delta * (twa - start_twa)
            self.polar_grid[twa][tws] = interpolated_stw
            print("Linear interpolation at twa = %d, tws = %d to stw = %d" % (twa, tws, interpolated_stw))

    def extend_to_extremes(self, tws, start_twa, to_increase):
        end_twa = (
            min(180, start_twa + BoatPolar.MAX_BLIND_INTERPOLATION_DISTANCE) if to_increase
            else max(0, start_twa - BoatPolar.MAX_BLIND_INTERPOLATION_DISTANCE)
        )
        print("Extending to extremes for TWS = %d from TWA = %d to TWA = %d" % (tws, start_twa, end_twa))
        known_stw = self.polar_grid[start_twa][tws]

        # Compute the decrement for each TWA step
        steps = abs(start_twa-end_twa)
        if steps > 0:
            decrement_per_step = known_stw / steps

            if decrement_per_step>0:
                # Ensure to don't touch anything existing
                go_on_with_exec = True
                for i in range(1, steps+1):
                    twa_index_to_edit = start_twa + i if to_increase else start_twa - i
                    if self.polar_grid[twa_index_to_edit][tws] != 0:
                        go_on_with_exec = False
                        break

                if go_on_with_exec:
                    # Apply the decrement at each step
                    for i in range(1, steps+1):
                        # Compute the index to be edited starting from the origin and from the number of previous steps
                        twa_index_to_edit = start_twa + i if to_increase else start_twa - i
                        self.polar_grid[twa_index_to_edit][tws] = max(known_stw - decrement_per_step * i, 0)

    def export_polar_file(self):
        filename = self.polar_file + str(time()) + ".pol"
        # Determine what TWS columns have STW values different from 0
        tws_to_include = [tws for tws in range(81) if any(self.polar_grid[twa][tws] > 0 for twa in range(181))]

        # Determine what AWA rows have STW values different from 0
        twa_to_include = [twa for twa in range(181) if any(self.polar_grid[twa][tws] > 0 for tws in tws_to_include)]

        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)

            # Write the header with valid TWS
            writer.writerow(['TWA/TWS'] + [str(tws) for tws in tws_to_include])

            # For each valid TWS, write its valid AWA rows
            for twa in twa_to_include:
                row = [self.polar_grid[twa][tws] for tws in tws_to_include]
                writer.writerow([twa] + row)
