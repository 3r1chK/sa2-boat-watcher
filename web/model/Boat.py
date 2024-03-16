from web.model.BoatLog import BoatLog
from web.model.BoatPolar import BoatPolar
from web.model.database import db


class Boat(db.Model):
    __tablename__ = 'boats'

    id = db.Column(db.Integer, primary_key=True)
    boat_type_id = db.Column(db.Integer, db.ForeignKey('boat_types.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    sa2verified = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship
    # This will require a foreign key in the BoatPolar. and BoatLog models
    polar = db.relationship(BoatPolar, uselist=False, backref='boat')
    logs = db.relationship(BoatLog, backref='boat')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'boat_type': self.boat_type_id,
            'sa2verified': self.sa2verified,
            'polar': self.polar.to_dict() if self.polar else None,
            'logs': [log.to_dict() for log in self.logs]
        }
