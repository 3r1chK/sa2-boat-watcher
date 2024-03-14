from web.model.database import db


class BoatLog(db.Model):
    __tablename__ = 'boat_logs'

    id = db.Column(db.Integer, primary_key=True)

    # Define the relationship to the Boat model
    boat_id = db.Column(db.Integer, db.ForeignKey('boats.id'), nullable=False)

    # Data fields
    ubtnr = db.Column(db.Integer)
    foilleft = db.Column(db.Boolean)
    foilright = db.Column(db.Boolean)
    aws = db.Column(db.Float)  # Apparent Wind Speed
    tws = db.Column(db.Float)  # True Wind Speed
    twa = db.Column(db.Float)  # True Wind Angle
    sog = db.Column(db.Float)  # Speed Over Ground
    cog = db.Column(db.Float)  # Course Over Ground
    twd = db.Column(db.Float)  # True Wind Direction
    hdg = db.Column(db.Float)  # Heading
    awa = db.Column(db.Float)  # Apparent Wind Angle
    heeldegrees = db.Column(db.Float)
    waterballast = db.Column(db.Float)
    keelangle = db.Column(db.Float)
    weatherhelm = db.Column(db.Float)
    boattype = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    misnr = db.Column(db.Integer)
    boatname = db.Column(db.String(255))
    backstay = db.Column(db.Float)
    # You might want to serialize the 'sails' data if it's a list or a complex object
    sails = db.Column(db.Text)
    voyage = db.Column(db.String(255))
    raceorchallenge = db.Column(db.String(255))
    drift = db.Column(db.Float)
    spd = db.Column(db.Float)
    divedegrees = db.Column(db.Float)
