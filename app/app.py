"""
This file holds all the resources for user from registration to borrow books and return books
"""
import datetime
import re
from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token,\
    get_jwt_identity, create_refresh_token, get_raw_jwt, jwt_refresh_token_required
import random


from .models import User, Book, Borrow, UserBorrowHistory, Admin, RevokedToken

app = Flask(__name__)
api = Api(app, prefix='/api/v1')
app.secret_key = 'mysecretkeyishere'
app.config['JWT_SECRET_KEY'] = '123$%##ghdsertes#$2'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config.setdefault('JWT_TOKEN_LOCATION', ['headers'])
app.config.setdefault('JWT_HEADER_NAME', 'Authorization')
app.config.setdefault('JWT_HEADER_TYPE', '')
app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', datetime.timedelta(minutes=15))
app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', datetime.timedelta(days=30))
app.config.setdefault('JWT_ALGORITHM', 'HS256')
app.config['JWT_IDENTITY_CLAIM'] = ['identity']
app.config['JWT_USER_CLAIMS'] = ['user_claims']
jwt = JWTManager(app)
app.url_map.strict_slashes = False
PROPAGATE_EXCEPTIONS = True


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklist(jti)

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
add_book_parser.add_argument('no_of_copies', type=int, help='Enter the number of copies')

edit_book_parser = add_book_parser.copy()
delete_book_parser = reqparse.RequestParser()


@app.route('/')
def index():
    """It holds the homepage url and renders the generated html doc for api documentation"""
    return render_template('docs.html')


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
                create_user = User(user_id, email, username, password)
                create_user.user_id = user_id
                create_user.email = email
                create_user.username = username
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
            ret_token = {
                'access_token': create_access_token(identity=email),
                'refresh_token': create_refresh_token(identity=email)
            }
            return {'Message': "Successfully logged in.", "Authentication token": ret_token}, 200
        return {"Message": "Wrong password!"}, 401


class UserLogout(Resource):
    """
        It holds user logout functionality
    """
    @jwt_required
    def post(self):
        """Post Method to logout user"""
        jti = get_raw_jwt()['jti']
        revoked_token = RevokedToken(jti=jti)
        revoked_token.add()
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
        if not reset_user:
            return {"Message": "The email does not exist."}, 404
        password = args['password']
        password_length = re.match("[A-Za-z0-9@#$%^&+=]{8,}", password.strip())
        if not password_length:
            return {"Message": "Password is short!"}, 400
        reset_user.email = email
        reset_user.set_password(password)
        reset_user.user_serializer()
        return {"Message": "Password is reset successfully."}, 200


class AddBook(Resource):
    """
    Contains all the methods to add book, list all books
    """
    @jwt_refresh_token_required
    def post(self, user_id):
        print("yes")
        """Post method to allow addition of book"""
        args = add_book_parser.parse_args()
        current_user = get_jwt_identity()
        refresh_token = {
            'access_token': create_access_token(identity=current_user)
        }
        confirm_admin = Admin.get_admin(user_id)
        if refresh_token and confirm_admin:
            no_of_copies = args['no_of_copies']
            book_quantity = 0
            while book_quantity <= no_of_copies:
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
                    new_book = Book(book_id, book_title, authors, year)
                    new_book.book_id = book_id
                    new_book.book_title = book_title
                    new_book.authors = authors
                    new_book.year = year
                    new_book.save_book()
                    book_quantity += 1
                    result = new_book.book_serializer()
                    return {"Message": "The book was added successfully.", "Book Added": result}, 201

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
    @jwt_refresh_token_required
    def put(self, book_id, user_id):
        """Put method to edit already existing book"""
        args = edit_book_parser.parse_args()
        current_user = get_jwt_identity()
        refresh_token = {
            'access_token': create_access_token(identity=current_user)
        }
        confirm_admin = Admin.get_admin(user_id)
        if refresh_token and confirm_admin:
            if not book_id:
                return {"Message": "The book is not found."}, 404
            get_book = Book.get_book_by_id(book_id)
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

    @jwt_refresh_token_required
    def delete(self, book_id, user_id):
        """Delete method to delete a single book"""
        current_user = get_jwt_identity()
        refresh_token = {
            'access_token': create_access_token(identity=current_user)
        }
        confirm_admin = Admin.get_admin(user_id)
        if refresh_token and confirm_admin:
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


class BorrowBook(Resource):
    """
    This class hold function for user can borrow, return book and check history
    """
    @jwt_refresh_token_required
    def post(self, book_id, user_id):
        """Post method for user to borrow book"""
        current_user = get_jwt_identity()
        refresh_token = {
            'access_token': create_access_token(identity=current_user)
        }
        confirm_user = User.get_user_by_id(user_id)
        if refresh_token and confirm_user:
            get_book = Book.get_book_by_id(book_id)
            if not get_book:
                return {"Message": "The book you want to borrow is unavailable."}, 404
            borrow_book = Borrow.save_borrowed_book(book_id)
            return {"Message": "successfully borrowed the book", "Book": borrow_book}, 202

    @jwt_refresh_token_required
    def put(self, book_id, user_id):
        """Put method to allow user return book"""
        current_user = get_jwt_identity()
        refresh_token = {
            'access_token': create_access_token(identity=current_user)
        }
        confirm_user = User.get_user_by_id(user_id)
        if refresh_token and confirm_user:
            return_book = Borrow.get_borrow_book_by_id(book_id)
            if return_book:
                Borrow.return_borrowed_book(book_id)
                return {"Message": "You have returned the book successfully."}, 202


class BorrowHistory(Resource):
    """
    This class contains the book borrowing history
    """
    @jwt_required
    def get(self, user_id):
        """It returns the users borrowing history"""
        current_user = get_jwt_identity()
        confirm_id = User.get_user_by_id(user_id)
        if current_user and confirm_id:
            borrow_history_books = UserBorrowHistory.get_borrow_history()
            if not borrow_history_books:
                return {"Message": "You have not borrowed any book."}, 404
            results = [borrow_history_book.borrowing_history_serializer()
                       for borrow_history_book in borrow_history_books]
            return {"Borrowed Books": results}, 200


class UnReturnedBooks(Resource):
    """Contains a list of books that a user has not yet returned"""
    @jwt_required
    def get(self, user_id):
        """User history of books not yet returned"""
        current_user = get_jwt_identity()
        confirm_id = User.get_user_by_id(user_id)
        if current_user and confirm_id:
            un_returned_books = UserBorrowHistory.get_books_not_yet_returned()
            if not un_returned_books:
                return {"Message": "Currently you do not have un-returned books"}, 404
            results = [un_returned_book.borrowing_history_serializer()
                       for un_returned_book in un_returned_books]
            return {"Un-returned books": results}, 200


# The registration of all endpoints
api.add_resource(UserRegistration, '/auth/register/')
api.add_resource(UserLogin, '/auth/login/')
api.add_resource(UserLogout, '/auth/logout/')
api.add_resource(ResetPassword, '/auth/reset-password/')

api.add_resource(AddBook, '/books/')
api.add_resource(SingleBook, '/books/<int:book_id>/')

api.add_resource(BorrowBook, '/users/books/<int:book_id>/')
api.add_resource(BorrowHistory, '/users/books')
api.add_resource(UnReturnedBooks, '/users/books?returned=false')
