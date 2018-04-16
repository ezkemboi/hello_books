"""
This file holds all the resources for user from registration to borrow books and return books
"""
import re
from flask import render_template, request
from functools import wraps
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
import random
from .models import User, Book, Borrow, BlacklistToken
from app import app

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
            return {"Error": "Token is missing. Please provide a valid token"}, 401
        try:
            response = User.decode_token(token)
            current_user = User.query.filter_by(user_id=response).first()
        except Exception:
            return {"Error": "please login again"}, 401
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

            return {"Message": "No valid token found"}, 401
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
        password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password.strip())
        if not password_length:
            return {"Message": "Password is short!"}, 400
        hashed_password = generate_password_hash(reset_user.password, method='sha256')
        reset_user.password = hashed_password
        reset_user.update_user()
        return {"Message": "Password is reset successfully."}, 200


class AddBook(Resource):
    """
    Contains all the methods to add book, list all books
    """
    @token_required
    def post(self, current_user):
        """Post method to allow addition of book"""
        args = add_book_parser.parse_args()
        book_id = random.randint(1111, 9999)
        book_title = args['book_title']
        authors = args['authors']
        year = args['year']
        existing_id = Book.query.filter_by(book_id=book_id).first()
        if not book_title or not authors:
            return {"Message": "Please fill all the details."}, 400
        if existing_id:
            return {"Message": "A book with that id already exist."}, 400
        new_book = Book(book_id=book_id, book_title=book_title, authors=authors, year=year)
        new_book.save_book()
        result = new_book.book_serializer()
        return {"Message": "The book was added successfully.", "Book Added": result}, 201

    def get(self):
        """Get method to get all books"""
        books = Book.query.all()
        if not books:
            return {"Message": "Books not found"}, 404
        results = [book.book_serializer() for book in books]
        return {"Books": results}, 200


class SingleBook(Resource):

    """
    Contains all activities of a single book, including editing, getting and removing a book.
    """
    @token_required
    def put(self, current_user, book_id):
        """Put method to edit already existing book"""
        args = edit_book_parser.parse_args()
        if not book_id:
            return {"Message": "The book is not found."}, 404
        get_book = Book.query.filter_by(book_id=book_id).first()
        book_title = args['book_title']
        authors = args['authors']
        year = args['year']
        if get_book and get_book.book_id == book_id:
            get_book.book_title = book_title
            get_book.authors = authors
            get_book.year = year
            get_book.update_book()
            edited_book = get_book.book_serializer()
            return {"Success": edited_book}, 200

    @token_required
    def delete(self, current_user, book_id):
        """Delete method to delete a single book"""
        get_book_id = Book.query.filter_by(book_id=book_id).first()
        if get_book_id:
            get_book_id.delete_book()
            return {"Message": "The book was deleted successfully."}
        return {"Error": "Book not found."}, 404

    def get(self, book_id):
        """Get method for a single book"""
        book = Book.query.filter_by(book_id=book_id).first()
        if book:
            result = book.book_serializer()
            return {"Book": result}, 200
        return {"Error": "Book not found."}, 404


class BorrowBook(Resource):
    """
    This class hold function for user can borrow, return book and check history
    """
    method_decorators = [token_required]

    def post(self, current_user, book_id):
        """Post method for user to borrow book"""
        available_book = Book.query.filter_by(book_id=book_id).first()
        if available_book:
            borrow_book = Borrow(borrow_id=random.randint(1111, 9999),
                                 book_id=book_id, user_id=current_user.user_id)
            borrow_book.save_borrowed_book()
            result = borrow_book.borrow_serializer()
            return {"Book borrowed": result}, 202

    def put(self, current_user, book_id):
        """Put method to allow user return book"""
        return_book = Borrow.query.filter_by(book_id=book_id).first()
        if return_book:
            Borrow.return_borrowed_book(book_id)
            return {"Message": "You have returned the book successfully."}, 202


class BorrowHistory(Resource):
    """
    This class contains the book borrowing history
    """
    method_decorators = [token_required]

    def get(self, current_user, user_id):
        """It returns the users borrowing history"""
        all_borrowed_books = Borrow.query.filter_by(user_id=user_id)
        if not all_borrowed_books:
            return {"Message": "You have not borrowed any book."}, 404
        results = [user_borrows.borrow_serializer()
                   for user_borrows in all_borrowed_books]
        return {"Borrowing history list": results}


class UnReturnedBooks(Resource):
    """Contains a list of books that a user has not yet returned"""
    method_decorators = [token_required]

    def get(self, current_user):
        """User history of books not yet returned"""
        # un_returned_books = Borrow.query.filter(Borrow.return_status.is_(False)).all()
        un_returned_books = Borrow.query.filter_by(user_id=current_user.user_id, return_status=False)
        return un_returned_books

