from web.model.BoatType import BoatType


class BoatTypeService:

    def __init__(self):
        pass

    @staticmethod
    def get_all():
        return BoatType.query.all()

    @staticmethod
    def get_from_name(type_name: str):
        return BoatType.query.filter_by(type_name=type_name).first()
