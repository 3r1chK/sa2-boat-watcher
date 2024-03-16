# TO BE EXECUTED ONCE!!!
import configparser
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Setting up configs
app.config['UPLOAD_FOLDER'] = '/tmp/'  # Ensure this directory exists
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit for uploads
config = configparser.ConfigParser()
config.read('web/web_conf.ini')     # TODO: replace with Flask app config!

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + config['Database'].get("sqlite3_path")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize db with app
db.init_app(app)


## Make sure to call this only once, not every time app.py is imported
with app.app_context():
    db.create_all()
