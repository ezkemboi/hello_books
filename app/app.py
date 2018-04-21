"""
This file holds all the resources for user from registration to borrow books and return books
"""
import re
from flask import Flask, session
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token,\
    get_jwt_identity
import random


from app.models import User, Book

app = Flask(__name__)
api = Api(app, prefix='/api/v1')
app.secret_key = 'mysecretkeyishere'
jwt = JWTManager(app)
app.url_map.strict_slashes = False

# Define all parsers for all classes
login_parser = reqparse.RequestParser()
login_parser.add_argument('email', type=str, help='Please enter the email', required=True)
login_parser.add_argument('password', type=str, help='please enter the password', required=True)

register_parser = login_parser.copy()
register_parser.add_argument('username', type=str, help='Please enter the username', required=True)

reset_password_parser = login_parser.copy()

add_book_parser = reqparse.RequestParser()
add_book_parser.add_argument('book_title', type=str, help='Please enter the book title', required=True)
add_book_parser.add_argument('authors', type=str, help='Please enter the authors name', required=True)
add_book_parser.add_argument('year', type=int, help='Please enter the year published')

edit_book_parser = add_book_parser.copy()
delete_book_parser = reqparse.RequestParser()


class UserRegistration(Resource):
    """It holds user registration functionality"""

    def post(self):
        """Post method for user registration"""
        args = register_parser.parse_args()
        user_id = random.randint(1111, 9999)
        email = args['email']
        username = args['username']
        password = args['password']
        user = User.get_user_by_email(email)
        valid_email = re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email.strip())
        valid_username = re.match("[A-Za-z0-9@#$%^&+=]{4,}", username.strip())
        password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password.strip())
        if not email or not username or not password:
            return {"Message": "Provide email, username and password!"}, 400
        username = User.get_user_by_username(username)
        if username:
            return {"Message": "The username is already taken!"}, 409
        if not user:
            if not valid_email:
                return {"Message": "Please provide a valid email!"}, 400
            elif not valid_username:
                return {"Message": "Username need to be more than 4 characters!"}, 400
            elif not password_length:
                return {"Message": "Password is short!"}, 400
            else:
                create_user = User()
                create_user.user_id = user_id
                create_user.email = email
                create_user.set_password(password)
                create_user.save_user()
                return {"Message": "The User is successfully Registered."}, 201
        return {"Message": "The user is already registered."}, 422


class UserLogin(Resource):
    """It holds user login functionality"""

    def post(self):
        """The post method logs in user"""
        args = login_parser.parse_args()
        email = args['email']
        password = args['password']
        if not email or not password:
            return {"Message": "Fill all fields!"}, 400
        log_in_user = User.get_user_by_email(email)
        if not log_in_user:
            return {"Message": "Invalid email!"}, 403
        elif log_in_user and log_in_user.check_password(password):
            access_token = create_access_token(identity=email)
            session['logged_in'] = True
            return {'Message': "Successfully logged in.", "Access token": access_token}, 200
        return {"Message": "Wrong password!"}, 401


class UserLogout(Resource):
    """
        It holds user logout functionality
    """
    def post(self):
        """Post Method to logout user"""
        session['logged_in'] = False
        return {"Message": "Your logged out."}, 200


class ResetPassword(Resource):
    """
        It holds user reset password functionality
    """
    def post(self):
        """The method allow user to reset password"""
        args = reset_password_parser.parse_args()
        email = args['email']
        reset_user = User.get_user_by_email(email)
        if reset_user:
            password = args['password']
            password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password.strip())
            if password_length:
                reset_user.email = email
                reset_user.set_password(password)
                reset_user.user_serializer()
                return {"Message": "Password is reset successfully."}, 200
            return {"Message": "Password is short!"}, 400
        return {"Message": "The email does not exist."}, 404


class AddBook(Resource):
    """
    Contains all the methods to add book, list all books
    """
    def post(self):
        """Post method to allow addition of book"""
        args = add_book_parser.parse_args()
        book_id = random.randint(1111, 9999)
        book_title = args['book_title']
        authors = args['authors']
        year = args['year']
        existing_id = Book.get_book_by_id(book_id)
        if not book_title or not authors:
            return {"Message": "Please fill all the details."}, 400
        if existing_id:
            return {"Message": "A book with that id already exist."}, 400
        elif not existing_id:
            new_book = Book()
            new_book.book_id = book_id
            new_book.book_title = book_title
            new_book.authors = authors
            new_book.year = year
            new_book.save_book()
            return {"Message": "The book was added successfully."}, 201

    def get(self):
        """Get method to get all books"""
        available_books = Book.get_all_books()
        if not available_books:
            return {"Message": "Books not found."}, 404
        results = [available_book.book_serializer() for available_book in available_books]
        return {"Books": results}, 200


class SingleBook(Resource):

    """
    Contains all activities of a single book, including editing, getting and removing a book.
    """
    def put(self, book_id):
        """Put method to edit already existing book"""
        args = edit_book_parser.parse_args()
        get_book = Book.get_book_by_id(book_id)
        book_title = args['book_title']
        authors = args['authors']
        year = args['year']
        if get_book and get_book.book_id == book_id:
            get_book.book_title = book_title
            get_book.authors = authors
            get_book.year = year
            edited_book = get_book.book_serializer()
            return {"Success": edited_book}, 200
        return {"Message": "The book is not found."}, 404

    def delete(self, book_id):
        """Delete method to delete a single book"""

        if book_id:
            get_book_id = Book.get_book_by_id(book_id)
            if get_book_id:
                get_book_id.delete_book()
                return {"Message": "The book was deleted successfully."}, 204
            return {"Error": "Book not found."}, 404

    def get(self, book_id):
        """Get method for a single book"""
        if book_id:
            get_book = Book.get_book_by_id(book_id)
            if get_book:
                result = get_book.book_serializer()
                return {"Book": result}, 200
            return {"Error": "Book not found."}, 404


class Borrow(Resource):
    """
    This class hold function for user can borrow, return book and check history
    """

    def post(self, book_id):
        """Post method for user to borrow book"""
        get_book = Book.get_book_by_id(book_id)
        if get_book:
            Book.borrow_book(book_id)
            return {"Message": "successfully borrowed a book"}, 202
        return {"Message": "The book you want to borrow is unavailable."}, 404

# The registration of all endpoints
api.add_resource(UserRegistration, '/auth/register/')
api.add_resource(UserLogin, '/auth/login/')
api.add_resource(UserLogout, '/auth/logout/')
api.add_resource(ResetPassword, '/auth/reset-password/')

api.add_resource(AddBook, '/books/')
api.add_resource(SingleBook, '/books/<int:book_id>/')
api.add_resource(Borrow, '/users/books/<int:book_id>/')
