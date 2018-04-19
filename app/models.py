"""
The file contains all data models for the application
"""
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model):
    """
    Hold data for user
    """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    __mapper_args__ = {'polymorphic_identity': username}
    borrows = db.relationship('Borrow', backref='users', lazy='dynamic')

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

    def set_password(self, password):
        """Method to set hashed password for the user"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Method to check that password is valid"""
        return check_password_hash(self.password, password)

    @staticmethod
    def get_user_by_email(email):
        """This method allow to filter users by their email"""
        return User.query.filter_by(email=email).first

    @staticmethod
    def get_user_by_username(username):
        """This method allow filter of users by their username"""
        return User.query.filter_by(username=username).first

    @staticmethod
    def get_user_by_id(user_id):
        """Get the user by user_id"""
        return User.query.get(user_id)

    def save_user(self):
        """The method is used to save the user in the list"""
        db.session.add(self)
        db.session.commit()


class Admin(User):
    """
    This class inherit from class user and contains admin methods
    """
    __mapper_args__ = {'polymorphic_identity': 'admin'}
    admin = db.Column(db.Boolean, default=True)

    @staticmethod
    def get_admin(user_id):
        return Admin.query.get(user_id)


class Book(db.Model):
    """
    Hold details for books
    """

    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String)
    authors = db.Column(db.String)
    year = db.Column(db.String)
    borrows = db.relationship('Borrow', backref='books', lazy='dynamic')

    def __init__(self, book_id, book_title, authors, year):
        """This method initializes book details"""
        self.book_id = book_id
        self.book_title = book_title
        self.authors = authors
        self.year = year

    def __repr__(self):
        """Represent object instance on query"""
        return "<Book_id {}>".format(self.book_id)

    def book_serializer(self):
        """This is a serialized book details stored in dict"""
        book_details = {
            'book_id': self.book_id,
            'book_title': self.book_title,
            'authors': self.authors,
            'year': self.year
        }
        return book_details

    @staticmethod
    def get_book_by_id(book_id):
        """This method allow user to get single book using book_id"""
        return Book.query.get(book_id)

    @staticmethod
    def get_all_books():
        """This method allow user to access all books"""
        return Book.query.all()

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    histories = db.relationship('UserBorrowHistory', backref='borrows', lazy='dynamic')

    def __init__(self, borrow_id, user_id, book_id):
        """Initialize borrow details"""
        self.borrow_id = borrow_id
        self.user_id = user_id
        self.book_id = book_id

    def __repr__(self):
        """Represent object instance on query"""
        return "<Borrow_id {}>".format(self.borrow_id)

    def save_borrowed_book(self):
        """Save a book borrowed by the user"""
        db.session.add(self)
        db.session.commit()

    def return_borrowed_book(self):
        """Method to allow user return book borrowed"""
        db.session.delete(self)
        db.commit()

    @staticmethod
    def get_all_borrowed():
        """The method allow user get book that need to borrow"""
        return Borrow.query.all()

    @staticmethod
    def get_borrow_book_by_id(book_id):
        """Allow user get a single book borrowed"""
        return Borrow.query.get(book_id)


class UserBorrowHistory(db.Model):
    """Holds the history of the past books borrowed by user"""

    __tablename__ = 'histories'

    borrow_id = db.Column(db.Integer, db.ForeignKey('borrows.borrow_id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    return_status = db.Column(db.Boolean, default=False)

    def __init__(self, borrow_id, book_id):
        """Initialize the user history borrowing list"""
        self.borrow_id = borrow_id
        self.book_id = book_id

    def __repr__(self):
        """Represent object instance on query"""
        return "<Borrow_id {}>".format(self.borrow_id)

    def borrowing_history_serializer(self):
        """Make a serializer for borrow history for user"""
        borrow_history_details = {
            'borrow_id': self.borrow_id,
            'book_id': self.book_id
        }
        return borrow_history_details

    def save_borrow_history(self):
        """Save books borrowed by the user"""
        db.session.save(self)
        db.session.commit()

    @staticmethod
    def get_borrow_history():
        """Get all books borrowed by the user"""
        return UserBorrowHistory.query.all()

    @staticmethod
    def get_books_not_yet_returned():
        return UserBorrowHistory.query.filter(
            UserBorrowHistory.return_status.is_(False)).all()


class RevokedToken(db.Model):
    """Holds the tokens"""
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklist(cls, jti):
        confirm_blacklist = cls.query.filter_by(jti=jti).first()
        return bool(confirm_blacklist)
