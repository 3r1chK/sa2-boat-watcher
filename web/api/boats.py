from flask import request, jsonify, abort, Blueprint

from web.controller.BoatService import BoatService
from web.model.database import db
from web.model.Boat import Boat


boats_api = Blueprint('api_boats', __name__)


@boats_api.route('/boats', methods=['GET'])
def get_boats():
    boats = Boat.query.all()
    return jsonify([boat.to_dict() for boat in boats]), 200


@boats_api.route('/boats/<int:boat_id>', methods=['GET'])
def get_boat(boat_id):
    boat = Boat.query.get(boat_id)
    if boat is not None:
        return jsonify(boat.to_dict()), 200
    else:
        abort(404)


@boats_api.route('/boats', methods=['POST'])
def create_boat():
    if not request.json or 'name' not in request.json:
        abort(400)
    boat = Boat(name=request.json['name'])
    db.session.add(boat)
    db.session.commit()
    return jsonify(boat.to_dict()), 201


@boats_api.route('/boats/<int:boat_id>', methods=['PUT'])
def update_boat(boat_id):
    boat = Boat.query.get(boat_id)
    if boat is None:
        abort(404)
    if not request.json:
        abort(400)

    boat.name = request.json.get('name', boat.name)

    db.session.commit()
    return jsonify(boat.to_dict())


@boats_api.route('/boats/<int:boat_id>', methods=['DELETE'])
def delete_boat(boat_id):
    boat = Boat.query.get(boat_id)
    if boat is None:
        abort(404)
    db.session.delete(boat)
    db.session.commit()
    return jsonify({'result': True})


@boats_api.route('/boats/verify/<int:boat_id>', methods=['PUT'])
def verify_boat(boat_id):
    try:
        if BoatService.verify_by_id(boat_id):
            return jsonify({"success": True, "message": "Boat verified successfully."}), 200
        else:
            return jsonify({"success": False, "message": "Can't verify this boat."}), 422
    except Exception as e:
        print("Exception in verify_boat: ", e)
        return jsonify({"success": False, "message": str(e)}), 500

