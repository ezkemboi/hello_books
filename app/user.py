"""
This file holds all the resources for user from registration to borrow books and return books
"""
import re
from flask import render_template, request
from functools import wraps
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash
import random

from .models import User, BlacklistToken
from app import app
from .parsers import login_parser, register_parser, reset_password_parser


def token_required(function):
    """This function require token to access routes"""
    @wraps(function)
    def wrapper(*args, **kwargs):
        """Help get header token"""
        token = ''
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header
        if not token:
            return {"Message": "Token is missing. Please provide a valid token"}, 401
        try:
            response = User.decode_token(token)
            current_user = User.query.filter_by(user_id=response).first()
        except Exception:
            return {"Message": "Expired token, please login in again"}, 401
        return function(current_user, *args, **kwargs)
    return wrapper


@app.route('/')
def index():
    """It holds the homepage url and renders the generated html doc for api documentation"""
    return render_template('docs.html')


class UserRegistration(Resource):
    """It holds user registration functionality"""

    def post(self):
        """Post method for user registration"""
        args = register_parser.parse_args()
        email = args['email']
        username = args['username']
        password = args['password']
        user = User.query.filter_by(email=email).first()
        valid_email = re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email.strip())
        valid_username = re.match("[A-Za-z0-9@#$%^&+=]{4,}", username.strip())
        password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password.strip())
        hashed_password = generate_password_hash(password, method='sha256')
        if not email or not username or not password:
            return {"Message": "Provide email, username and password!"}, 400
        username = User.query.filter_by(username=username).first()
        if username:
            return {"Message": "The username is already taken!"}, 409
        if user:
            return {"Message": "The user is already registered."}, 422
        if not valid_email:
            return {"Message": "Please provide a valid email!"}, 400
        elif not valid_username:
            return {"Message": "Username need to be more than 4 characters!"}, 400
        elif not password_length:
            return {"Message": "Password is short!"}, 400
        else:
            create_user = User(user_id=random.randint(1111, 9999), email=email, username=username,
                               password=hashed_password)
            create_user.save_user()
            return {"Message": "The User is successfully Registered."}, 201


class UserLogin(Resource):
    """It holds user login functionality"""
    def post(self):
        """The post method logs in user"""
        args = login_parser.parse_args()
        email = args['email']
        password = args['password']
        if not email or not password:
            return {"Message": "Fill all fields!"}, 400
        log_in_user = User.query.filter_by(email=email).first()
        if not log_in_user:
            return {"Message": "Invalid email!"}, 403
        if check_password_hash(log_in_user.password, password):
            access_token = log_in_user.generate_token(log_in_user.user_id)
            if access_token:
                return {'Message': "Successfully logged in.", "Access_token": access_token.decode()}, 200


class UserLogout(Resource):
    """
        It holds user logout functionality
    """
    @token_required
    def post(self, current_user):
        """Post Method to logout user"""
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header
            if token:
                response = User.decode_token(token)
                if not isinstance(response, str):
                    blacklisted_token = BlacklistToken(token=token)
                    try:
                        blacklisted_token.save_token()
                        return {"Message": "Your logged out."}, 200
                    except Exception:
                        return {"Error": "Internal server error"}, 500


class ResetPassword(Resource):
    """
        It holds user reset password functionality
    """

    def post(self):
        """The method allow user to reset password"""
        args = reset_password_parser.parse_args()
        email = args['email']
        reset_user = User.query.filter_by(email=email).first()
        if not reset_user:
            return {"Message": "The email does not exist."}, 404
        password = args['password']
        hashed_password = generate_password_hash(password, method='sha256')
        password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password.strip())
        if not password_length:
            return {"Message": "Password is short!"}, 400
        reset_user.password = hashed_password
        reset_user.update_user()
        return {"Message": "Password is reset successfully."}, 200
