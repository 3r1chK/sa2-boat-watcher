from web.controller.BoatTypeService import BoatTypeService
from web.controller.Sa2ApiService import Sa2ApiService
from web.model.Boat import Boat
from web.model.database import db


class BoatService:

    def __init__(self):
        pass

    @staticmethod
    def get_by_id(boat_id: int):
        return Boat.query.filter_by(id=boat_id).first()

    @staticmethod
    def verify_by_id(boat_id: int):
        boat = BoatService.get_by_id(boat_id)
        if boat is None:
            raise Exception("Can't find boat with id {}".format(boat_id))
        sa2_boat_data = Sa2ApiService.get_boat_data(boat)
        if sa2_boat_data is None:
            raise Exception("Something went wrong retrieving boat data from sa2")
        if not sa2_boat_data:
            return False
        BoatService.update_from_sa2_data(boat, sa2_boat_data)
        return True

    @staticmethod
    def update_from_sa2_data(boat: Boat, sa2_data):
        if boat is None or sa2_data is None:
            raise Exception("Boat or SA2 api data are missing")
        boat_type = BoatTypeService.get_from_name(sa2_data.get('boattype'))
        if boat_type is None:
            raise Exception(f"SA2 boat type ({sa2_data.get('boattype')}) is not registered in the system,"
                            f" so we can't complete boat verification.")
        boat.type = boat_type   # Set relationship with boat_type
        boat.sa2verified = True
        db.session.commit()
