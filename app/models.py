"""
The file contains all data models for the application
"""
import jwt
from datetime import datetime, timedelta
from flask import current_app

from app import db


class User(db.Model):
    """
    Hold data for user
    """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    borrows = db.relationship('Borrow', backref='user', lazy='dynamic')

    def __init__(self, user_id, email, username, password):
        """This method initializes the required items"""
        self.user_id = user_id
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return "<User_id {}>".format(self.user_id)

    def user_serializer(self):
        """Serialize the user data"""
        user_details = {
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'password': self.password
        }
        return user_details

    def save_user(self):
        """The method is used to save the user in the list"""
        db.session.add(self)
        db.session.commit()

    def update_user(self):
        db.session.commit()

    def generate_token(self, user_id):
        """Generate token for user authentication"""
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=10),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            return jwt_string
        except Exception as e:
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decode the generated token via the authorization header"""
        try:
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return "This token is expired. Please login to get new token"
        except jwt.InvalidTokenError:
            return "Invalid token. Please register or login"


class Book(db.Model):
    """
    Hold details for books
    """

    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, unique=True)
    book_title = db.Column(db.String)
    authors = db.Column(db.String)
    year = db.Column(db.String)
    copies = db.Column(db.Integer)
    borrows = db.relationship('Borrow', backref='book', lazy='dynamic')

    def __init__(self, book_id, book_title, authors, year, copies):
        """This method initializes book details"""
        self.book_id = book_id
        self.book_title = book_title
        self.authors = authors
        self.year = year
        self.copies = copies

    def __repr__(self):
        """Represent object instance on query"""
        return "<Book_id {}>".format(self.book_id)

    def book_serializer(self):
        """This is a serialized book details stored in dict"""
        book_details = {
            'book_id': self.book_id,
            'book_title': self.book_title,
            'authors': self.authors,
            'year': self.year,
            'copies': self.copies
        }
        return book_details

    def save_book(self):
        """This method allow admin to save a book"""
        db.session.add(self)
        db.session.commit()

    def delete_book(self):
        """This method helps in deleting an existing book"""
        db.session.delete(self)
        db.session.commit()

    def update_book(self):
        """Update a book edited by the admin"""
        db.session.commit()


class Borrow(db.Model):
    """Class holding the models for borrow and history"""
    __tablename__ = 'borrows'

    borrow_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    book_id = db.Column(db.Integer, db.ForeignKey(Book.book_id))
    date_borrowed = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    return_time = db.Column(db.DateTime)
    returned = db.Column(db.Boolean)

    def __init__(self, borrow_id, user_id, book_id, returned, date_borrowed, due_date):
        """Initialize borrow details"""
        self.borrow_id = borrow_id
        self.user_id = user_id
        self.book_id = book_id
        self.returned = returned
        self.date_borrowed = date_borrowed
        self.due_date = due_date

    def __repr__(self):
        """Represent object instance on query"""
        return "<Borrow_id {}>".format(self.borrow_id)

    def borrow_serializer(self):
        """Serialize data for borrow"""
        borrow_details = {
            'borrow_id': self.borrow_id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'returned': self.returned,
            'date_borrowed': self.date_borrowed,
            'due_date': self.due_date
        }
        return borrow_details

    def save_borrowed_book(self):
        """Save a book borrowed by the user"""
        db.session.add(self)
        db.session.commit()

    def return_borrowed_book(self):
        db.session.commit()


class BlacklistToken(db.Model):
    """
    Create a table for blacklisted tokens
    """
    __tablename__ = "blacklisted_tokens"

    id = db.Column(db.Integer, primary_key=True)
    token = db.column(db.String)
    blacklisted = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        """Initialize token blacklist"""
        self.token = token
        self.blacklisted = datetime.utcnow()

    def save_token(self):
        """Save blacklisted token"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_blacklisted(token):
        blacklisted = BlacklistToken.query.filter_by(
            token=str(token)).first()
        if blacklisted:
            return True
        return False
