# BoatLog.py


class BoatLog:
    def __init__(self, data):
        self.ubtnr = data.get('ubtnr')
        self.foilleft = data.get('foilleft')
        self.foilright = data.get('foilright')
        self.aws = data.get('aws')  # Apparent Wind Speed
        self.tws = data.get('tws')  # True Wind Speed
        self.twa = data.get('twa')  # True Wind Angle
        self.sog = data.get('sog')  # Speed Over Ground
        self.cog = data.get('cog')  # Course Over Ground
        self.twd = data.get('twd')  # True Wind Direction
        self.hdg = data.get('hdg')  # Heading
        self.awa = data.get('awa')  # Apparent Wind Angle
        self.heeldegrees = data.get('heeldegrees')
        self.waterballast = data.get('waterballast')
        self.keelangle = data.get('keelangle')
        self.weatherhelm = data.get('weatherhelm')
        self.boattype = data.get('boattype')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.misnr = data.get('misnr')
        self.boatname = data.get('boatname')
        self.backstay = data.get('backstay')
        self.sails = data.get('sails')  # Lista di dettagli sulle vele
        self.voyage = data.get('voyage')
        self.raceorchallenge = data.get('raceorchallenge')
        self.drift = data.get('drift')
        self.spd = data.get('spd')
        self.divedegrees = data.get('divedegrees')
