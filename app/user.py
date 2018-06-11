"""
This file holds all the resources for user from registration to borrow books and return books
"""
import re
# from flask import render_template
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt, get_jwt_identity
import random

from app.models import User, RevokedToken, Borrow
from app import app
from app.parsers import login_parser, register_parser, reset_password_parser
from run import jwt

#
# @app.route('/')
# def index():
#     """It holds the homepage url and renders the generated html doc for api documentation"""
#     return render_template('docs.html')


class UserRegistration(Resource):
    """It holds user registration functionality"""

    def post(self):
        """Post method for user registration"""
        args = register_parser.parse_args()
        email = args['email']
        first_name = args['first_name']
        last_name = args['last_name']
        username = args['username']
        password = args['password']
        user = User.query.filter_by(email=email).first()
        valid_email = re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email.strip())
        valid_username = re.match("[A-Za-z0-9@#$%^&+=]{4,}", username.strip())
        password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password.strip())
        hashed_password = generate_password_hash(password, method='sha256')
        taken_username = User.query.filter_by(username=username).first()
        if taken_username is not None:
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
            create_user = User(user_id=random.randint(1111, 9999), email=email, first_name=first_name,
                               last_name=last_name, username=username, password=hashed_password)
            create_user.save_user()
            return {"Message": "The User is successfully Registered."}, 201


class UserLogin(Resource):
    """It holds user login functionality"""
    def post(self):
        """The post method logs in user"""
        args = login_parser.parse_args()
        email = args['email']
        password = args['password']
        log_in_user = User.query.filter_by(email=email).first()
        if not log_in_user:
            return {"Message": "Invalid email!"}, 403
        if check_password_hash(log_in_user.password, password):
            access_token = create_access_token(identity=log_in_user.user_id)
            return {'Message': "Successfully logged in.", "access_token": access_token}, 200


class UserLogout(Resource):
    """
        It holds user logout functionality
    """
    @jwt_required
    def post(self):
        """Post Method to logout user"""
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add_token()
            return {"Message": "You are logged out."}, 200
        except:
            return {"Message": "Something went wrong."}, 500


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
