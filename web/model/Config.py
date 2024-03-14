from web.model.database import db


class Config(db.Model):
    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(255), nullable=False)
