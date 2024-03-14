from web.model.BoatLog import BoatLog
from web.model.BoatPolar import BoatPolar
from web.model.database import db


class Boat(db.Model):
    __tablename__ = 'boats'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    boat_type = db.Column(db.String(255), nullable=False)

    # Relationship
    # This will require a foreign key in the BoatPolar.py and BoatLog models
    polar = db.relationship(BoatPolar, uselist=False, backref='boat')
    logs = db.relationship(BoatLog, backref='boat')
