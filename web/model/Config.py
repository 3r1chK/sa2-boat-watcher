from web.model.database import db


class Config(db.Model):
    __tablename__ = 'config'

    key = db.Column(db.String(255), primary_key=True, nullable=False)
    type = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(255), nullable=False)
