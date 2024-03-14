import os
import configparser
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from src.SaGetWeatherApi import SaGetWeatherApi
from src.TimeOffsetDetectorByLocation import TimeOffsetDetectorByLocation


app = Flask(__name__)

# Setting up configs
app.config['UPLOAD_FOLDER'] = '/tmp/'  # Ensure this directory exists
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit for uploads
config = configparser.ConfigParser()
config.read('web_conf.ini') # TODO: replace with Flask app config!


# Webapp routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('dashboard_base.html', active_page='home')


@app.route('/timeshift_detector', methods=['GET'])
def timeshift_detector():
    return render_template('timeshift_detector.html', active_page='timeshift_detector')


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
