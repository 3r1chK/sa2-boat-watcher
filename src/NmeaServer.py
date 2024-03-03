# NmeaServer.py
import socket
import threading
import pynmea2
from datetime import datetime


class NmeaServer:
    def __init__(self, host='localhost', port=10110):
        self.host = host
        self.port = port
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_running = False

    def start_server(self):
        """Starts the server to listen and accept new connections."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.server_running = True
        print(f"NMEA Server running on {self.host}:{self.port}")

        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()

    def accept_connections(self):
        """Handles accepting new client connections."""
        while self.server_running:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connected to {client_address}")
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        """Manages communication with a single client."""
        while self.server_running:
            try:
                # Here you can send NMEA messages to the client or handle any requests
                pass
            except ConnectionResetError:
                break
        client_socket.close()

    def broadcast_nmea_message(self, message):
        """Sends an NMEA message to all connected clients."""
        for client_socket in self.clients[:]:  # Create a copy of the list for safe iteration
            try:
                client_socket.sendall(message.encode('utf-8'))
            except BrokenPipeError:
                try:
                    client_socket.close()  # Close the socket
                except Exception as e:
                    print(f"Error closing socket: {e}")
                finally:
                    self.clients.remove(client_socket)  # Then remove it from the list

    def stop_server(self):
        """Stops the server and closes all connections."""
        self.server_running = False
        for client_socket in self.clients:
            client_socket.close()
        self.server_socket.close()
        print("NMEA Server stopped.")

    def send_boatlog(self, boat_log):
        """Converts a BoatLog into an NMEA message and sends it."""
        # Here the conversion of BoatLog to NMEA 0183 format should be implemented
        # For example, you might have a function that formats the log into an NMEA string
        nmea_message = self.generate_nmea_sentence(boat_log)
        self.broadcast_nmea_message(nmea_message)

########################################################################################################################
    @staticmethod
    def convert_to_nmea_format(coordinate, coordinate_type):
        """Converts latitude or longitude to NMEA format."""
        degrees = int(coordinate)
        minutes = (coordinate - degrees) * 60
        return (
            f"{degrees:02d}{minutes:07.4f}",
            'N' if coordinate_type == 'latitude' and coordinate >= 0 else 'S'
            if coordinate_type == 'latitude' else 'E' if coordinate >= 0 else 'W'
        )

    def generate_nmea_sentence(self, boat_log):
        # Convert latitude and longitude data to NMEA formats
        lat, lat_dir = self.convert_to_nmea_format(boat_log.latitude, 'latitude')
        lon, lon_dir = self.convert_to_nmea_format(boat_log.longitude, 'longitude')

        # Create a list of NMEA sentences based on available data
        nmea_sentences = []

        # GPRMC - Recommended Minimum Specific GPS/TRANSIT Data
        if hasattr(boat_log, 'sog') and hasattr(boat_log, 'cog') and hasattr(boat_log, 'date'):
            date_str = self.get_date()  # Assuming this function returns a date string in ddmmyy format
            time_str = '120000'  # Assuming a fixed time or you can modify to use actual time
            gprmc = pynmea2.RMC('GP', 'RMC', (
            time_str, 'A', lat, lat_dir, lon, lon_dir, str(boat_log.sog), str(boat_log.cog), date_str, '', ''))
            nmea_sentences.append(str(gprmc))

        # Manually created unsupported sentences
        # Example: GPVTG, GPHDT, IIMWV, IIMWD
        nmea_sentences.extend([
            f'$GPVTG,{boat_log.cog},T,,M,{boat_log.sog},N,,K,A',
            f'$GPHDT,{boat_log.hdg},T',
            f'$IIMWV,{boat_log.awa},R,{boat_log.aws},N,A',
            f'$IIMWV,{boat_log.twa},T,{boat_log.tws},N,A',
            f'$IIMWD,,,{boat_log.twd},,,{boat_log.tws},N,,M'
        ])

        # Adding checksum to each sentence
        for i in range(len(nmea_sentences)):
            sentence = nmea_sentences[i]
            if sentence.startswith('$'):
                checksum = pynmea2.NMEASentence.calculate_checksum(sentence)
                nmea_sentences[i] = f"{sentence}*{checksum}"

        # Combine all sentences with line terminators
        return '\r\n'.join(nmea_sentences) + '\r\n'

########################################################################################################################

    def generate_nmea_sentence_old(self, boat_log):
        # Convert latitude and longitude data to NMEA formats
        lat = self.convert_to_nmea_latitude(boat_log.latitude)
        lon = self.convert_to_nmea_longitude(boat_log.longitude)

        # Create a list of NMEA sentences based on available data
        nmea_sentences = [
            # GPRMC - Recommended Minimum Specific GPS/TRANSIT Data (lat, lon, sog, cog, date)
            f'$GPRMC,,A,{lat},,{lon},,{boat_log.sog},{boat_log.cog},{self.get_date()},,,,',
            # GPVTG - Track Made Good and Ground Speed (cog, sog, hdg)
            f'$GPVTG,{boat_log.cog},T,,M,{boat_log.sog},N,,K,A', f'$GPHDT,{boat_log.hdg},T',
            # MWV - Wind Speed and Angle (tws, twa, aws, awa)
            f'$IIMWV,{boat_log.awa},R,{boat_log.aws},N,A',  # Apparent Wind Speed and Angle
            f'$IIMWV,{boat_log.twa},T,{boat_log.tws},N,A',  # True Wind Speed and Angle
            # MWD - Wind Direction and Speed (twd)
            f'$IIMWD,,,{boat_log.twd},,,{boat_log.tws},N,,M'  # True Wind Direction and Speed
        ]

        # Adding checksum to each sentence
        for i in range(nmea_sentences.__len__()):
            checksum = NmeaServer.calculate_checksum(nmea_sentences[i])
            nmea_sentences[i] = f"{nmea_sentences[i]}*{checksum}"

        # Combine all sentences with line terminators
        return '\r\n'.join(nmea_sentences) + '\r\n'

    @staticmethod
    def convert_to_nmea_latitude(latitude):
        """Formats the latitude in NMEA format."""
        degrees = int(latitude)
        minutes = (latitude - degrees) * 60
        return f"{abs(degrees):02}{minutes:05.2f}"

    @staticmethod
    def convert_to_nmea_longitude(longitude):
        """Formats the longitude in NMEA format."""
        degrees = int(longitude)
        minutes = (longitude - degrees) * 60
        return f"{abs(degrees):03}{minutes:05.2f}"

    @staticmethod
    def get_date():
        """Returns the current date in NMEA 0183 format (DDMMYY)."""
        current_date = datetime.now()
        return current_date.strftime('%d%m%y')

    @staticmethod
    def calculate_checksum(sentence):
        """Calculates the NMEA checksum for a sentence."""
        # The checksum is the XOR of all the characters between '$' and '*'
        checksum = 0
        for char in sentence[1:]:
            checksum ^= ord(char)
        return f"{checksum:02X}"
