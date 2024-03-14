import os
import configparser
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from src.SaGetWeatherApi import SaGetWeatherApi
from src.TimeOffsetDetectorByLocation import TimeOffsetDetectorByLocation
from web.model.database import db
from web.model.Boat import Boat


def create_app(first_time=False):
    new_app = Flask(__name__)

    def delete_file_if_exists(file_path):
        """Delete a file if it exists."""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    # Setting up configs
    new_app.config['UPLOAD_FOLDER'] = '/tmp/'  # Ensure this directory exists
    new_app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit for uploads
    config = configparser.ConfigParser()
    config.read('web/web_conf.ini')     # TODO: replace with Flask app config!
    db_rel_path = config['Database'].get("sqlite3_path")

    new_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + db_rel_path
    print(new_app.config['SQLALCHEMY_DATABASE_URI'])
    new_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    new_app.config['sa2_watcher'] = config

    # Initialize db with app
    db.init_app(new_app)

    if first_time:
        delete_file_if_exists(db_rel_path)
        # Make sure to call this only once, not every time app.py is imported
        with new_app.app_context():
            db.create_all()

    return new_app


app = create_app(True)


# Webapp routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html', active_page='home')


@app.route('/timeshift_detector', methods=['GET'])
def timeshift_detector():
    return render_template('timeshift_detector.html', active_page='timeshift_detector')


@app.route('/routes', methods=['GET'])
def routes():
    return render_template('routes.html', active_page='routes')


@app.route('/boats', methods=['GET'])
def boats():
    # Create a new boat
    new_boat = Boat(name='Sailaway', boat_type="24 banane")
    db.session.add(new_boat)
    db.session.commit()
    return render_template('boats.html', active_page='boats')


@app.route('/races', methods=['GET'])
def races():
    return render_template('races.html', active_page='races')


@app.route('/polars', methods=['GET'])
def polars():
    return render_template('polars.html', active_page='polars')


@app.route('/alarms', methods=['GET'])
def alarms():
    return render_template('alarms.html', active_page='alarms')


@app.route('/detect_time_offset', methods=['POST'])
def detect_time_offset():
    if 'grib_file' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    file = request.files['grib_file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        try:
            # TODO: implement autonomous GRIB downloader!!
            api = SaGetWeatherApi(0, 0)
            detector = TimeOffsetDetectorByLocation(api, file_path, hours_to_spread=6)
            detector.launch_detector()
            detector.shift_grib_in_new_file()
            # TODO: Consider cleanup of uploaded file after processing if necessary
            return jsonify({"success": True, "message": "Time offset detection executed successfully."}), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
