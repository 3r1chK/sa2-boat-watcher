from web.model.database import db


class BoatType(db.Model):
    __tablename__ = 'boat_types'

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(255), nullable=False, unique=True)  # TODO: Should also be the key!
    hull_type = db.Column(db.String(50))
    length_over_all = db.Column(db.Float)
    length_waterline = db.Column(db.Float)
    beam = db.Column(db.Float)
    depth = db.Column(db.Float)
    minimum_depth = db.Column(db.Float)
    total_weight = db.Column(db.Float)
    ballast = db.Column(db.Float)
    max_waterballast_per_side = db.Column(db.Float)
    mast = db.Column(db.Float)
    sail_area_up_wind = db.Column(db.Float)
    max_sail_area = db.Column(db.Float)
    dl_ratio = db.Column(db.Float)
    sd_ratio = db.Column(db.Float)
    photo = db.Column(db.String(255))  # Assuming the path to the image is stored as a string

    # Relationships
    sails = db.relationship('Sail', backref='boat_type')
    boats = db.relationship('Boat', backref='type', lazy=True)
