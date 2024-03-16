from web.model.database import db


class Sail(db.Model):
    __tablename__ = 'sails'

    sail_name = db.Column(db.String(50), primary_key=True)
    boat_type_id = db.Column(db.Integer, db.ForeignKey('boat_types.id'), primary_key=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    sail_area = db.Column(db.Float)

    # Ensuring that each sail_name is unique for a boat_type
    __table_args__ = (db.UniqueConstraint('sail_name', 'boat_type_id', name='_sail_name_boat_type_uc'),)
