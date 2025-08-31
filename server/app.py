from flask import request, Response, Flask, jsonify, session, send_from_directory
from flask_mail import Mail, Message
from flask_cors import CORS, cross_origin
from blueprints.auth.auth import auth_bp
from blueprints.accident.accident import accident_bp
from blueprints.public.public import public_bp
from blueprints.emails.emails import emails

# AUTH AND MONGODB
from bson import ObjectId
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB (now using Atlas instead of localhost)
MONGO_URI = os.getenv("MONGO_URI")   # should be set in .env
client = MongoClient(MONGO_URI)
mongo_db = client.flask_database

# CLOUDINARY (configured via .env)
import cloudinary
import cloudinary.api

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/videos'

# JWT...
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

# MAIL...
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# ALL BLUEPRINTS...
app.register_blueprint(auth_bp)
app.register_blueprint(accident_bp)
app.register_blueprint(public_bp)
app.register_blueprint(emails)

# MongoDB Collections
accidents_collection = mongo_db.accidents
users_collection = mongo_db.users

# CORS (frontend on localhost:3000)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

if __name__ == '__main__':
    app.run(debug=True, port=8080)