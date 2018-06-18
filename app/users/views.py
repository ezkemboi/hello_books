"""
This file holds all the resources for user from registration to borrow books and return books
"""
import re
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
import random

from app.models import User, RevokedToken
from app.helpers.parsers import login_parser, register_parser, reset_password_parser
from run import jwt


class UserRegistration(Resource):
    """It holds user registration functionality"""

    def post(self):
        """Post method for user registration"""
        registration_args = register_parser.parse_args()
        email = registration_args['email'].strip().lower()
        first_name = registration_args['first_name']
        last_name = registration_args['last_name']
        username = registration_args['username'].strip()
        password = registration_args['password'].strip()
        user = User.query.filter_by(email=email).first()
        valid_email = re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)
        valid_username = re.match("[A-Za-z0-9@#$%^&+=]{4,}", username)
        password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password)
        taken_username = User.query.filter_by(username=username).first()
        if not first_name.strip() or not last_name.strip():
            return {"message": "First/last name should not be empty."}, 400
        if not valid_email:
            return {"message": "Please provide a valid email!"}, 400
        if not valid_username:
            return {"message": "Username need to be more than 4 characters!"}, 400
        if not password_length:
            return {"message": "Password is short!"}, 400
        if user:
            return {"message": "The user is already registered."}, 422
        if taken_username is not None:
            return {"message": "The username is already taken!"}, 409
        create_user = User(user_id=random.randint(1111, 9999), email=email, first_name=first_name, last_name=last_name,
                           username=username, password=generate_password_hash(password, method='sha256'))
        create_user.save_user()
        return {"message": "The User is successfully Registered."}, 201


class UserLogin(Resource):
    """It holds user login functionality"""
    def post(self):
        """The post method logs in user"""
        login_args = login_parser.parse_args()
        email = login_args['email'].strip()
        password = login_args['password'].strip()
        log_in_user = User.query.filter_by(email=email).first()
        if not password:
            return {"message": "Please enter password."}, 400
        if not log_in_user:
            return {"message": "Invalid email!"}, 403
        if check_password_hash(log_in_user.password, password):
            access_token = create_access_token(identity=log_in_user.user_id)
            return {'message': "Successfully logged in.", "access_token": access_token}, 200


class UserLogout(Resource):
    """
        It holds user logout functionality
    """
    @jwt_required
    def post(self):
        """Post Method to logout user"""
        jti = get_raw_jwt()['jti']
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add_token()
        return {"message": "You are logged out."}, 200


class ResetPassword(Resource):
    """
        It holds user reset password functionality
    """

    def post(self):
        """The method allow user to reset password"""
        reset_pswd_args = reset_password_parser.parse_args()
        email = reset_pswd_args['email'].strip()
        reset_user = User.query.filter_by(email=email).first()
        if not reset_user:
            return {"message": "The email does not exist."}, 404
        password = reset_pswd_args['password'].strip()
        hashed_password = generate_password_hash(password, method='sha256')
        password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password.strip())
        if not password_length:
            return {"message": "Password is short!"}, 400
        reset_user.password = hashed_password
        reset_user.update_user()
        return {"message": "Password is reset successfully."}, 200
