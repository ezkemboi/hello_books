"""
The file contains all data models for the application
"""
from datetime import datetime, timedelta

from app import db


class User(db.Model):
    """
    Hold data for user
    """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    borrows = db.relationship('Borrow', backref='user', lazy='dynamic')

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


class Book(db.Model):
    """
    Hold details for books
    """

    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, nullable=False)
    book_title = db.Column(db.String, nullable=False)
    authors = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    copies = db.Column(db.Integer, nullable=False)
    borrows = db.relationship('Borrow', backref='book', lazy='dynamic')

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

    borrow_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
    book_id = db.Column(db.Integer, db.ForeignKey(Book.book_id))
    date_borrowed = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    return_time = db.Column(db.DateTime)
    returned = db.Column(db.Boolean, nullable=False)

    def borrow_serializer(self):
        """Serialize data for borrow"""
        borrow_details = {
            'borrow_id': self.borrow_id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'returned': self.returned,
        }
        return borrow_details

    def save_borrowed_book(self):
        """Save a book borrowed by the user"""
        db.session.add(self)
        db.session.commit()

    def return_borrowed_book(self):
        db.session.commit()


class RevokedToken(db.Model):
    """
    Create a table for blacklisted tokens
    """
    __tablename__ = "revoked_tokens"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.column(db.String(80))

    def add_token(self):
        """Save blacklisted token"""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
