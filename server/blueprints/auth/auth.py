import hashlib
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Connect to MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
mongo_db = client.flask_database

# COLLECTIONS
accidents_collection = mongo_db.accidents
users_collection = mongo_db.users


# -------------------------
# LOGIN ROUTE
# -------------------------
@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    login_details = request.get_json()

    # Frontend sends `username` but it's actually the email
    user_from_db = users_collection.find_one({'email': login_details['username']})

    if user_from_db:
        # Encrypt the provided password for comparison
        encrypted_password = hashlib.sha256(
            login_details['password'].encode('utf-8')
        ).hexdigest()

        if encrypted_password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['email'])
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'msg': 'The username or password is incorrect'}), 401
    else:
        return jsonify({'msg': "User does not exist"}), 404


# -------------------------
# REGISTER ROUTE
# -------------------------
@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def register():
    new_user = request.get_json()

    # Encrypt password before saving
    new_user['password'] = hashlib.sha256(
        new_user["password"].encode('utf-8')
    ).hexdigest()

    # Expecting frontend to send `username` (but we save it as email too)
    email_value = new_user.get("username") or new_user.get("email")
    if not email_value:
        return jsonify({'msg': 'Email/username is required'}), 400

    new_user["email"] = email_value  # store in DB consistently

    # Check if user with same email already exists
    doc = users_collection.find_one({"email": email_value})

    if not doc:
        users_collection.insert_one(new_user)
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'User already exists'}), 409