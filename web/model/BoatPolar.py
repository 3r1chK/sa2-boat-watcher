from web.model.database import db


class BoatPolar(db.Model):
    __tablename__ = 'boat_polars'

    # Define the relationship to the Boat model
    boat_id = db.Column(db.Integer, db.ForeignKey('boats.id'), nullable=False)

    id = db.Column(db.Integer, primary_key=True)
    polar_file = db.Column(db.String(255))
    # Additional fields, such as the polar grid, might be stored in a serialized
    # format if they don't map directly to a database column type
