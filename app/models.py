"""
The file contains all data models for the application
"""
from app import db


class Borrow(db.Model):
    """Association table of borrow. Store all books borrowed by user."""
    ___tablename__ = 'borrows'

    borrow_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id'), primary_key=True)
    book_id = db.Column(db.String, db.ForeignKey('books.book_id'), primary_key=True)
    date_borrowed = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    return_time = db.Column(db.DateTime)
    returned = db.Column(db.Boolean, nullable=False)
    book = db.relationship("Book", backref="user_borrows")
    user = db.relationship("User", backref="book_borrows")

    def borrow_serializer(self):
        """Serialize data for borrow"""
        borrow_details = {
            'Borrow Id': self.borrow_id,
            'Book Id': self.book_id,
            'User Id': self.user_id,
            'Return Status': self.returned,
        }
        return borrow_details

    def save_borrowed_book(self):
        """Save a book borrowed by the user"""
        db.session.add(self)
        db.session.commit()

    def return_borrowed_book(self):
        db.session.commit()


class User(db.Model):
    """
    Hold data for user
    """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    books = db.relationship('Book', secondary='borrow')

    def user_serializer(self):
        """Serialize the user data"""
        user_details = {
            'User Id': self.user_id,
            'Email': self.email,
            'First Name': self.first_name,
            'Last Name': self.last_name,
            'Username': self.username,
            'Password': self.password
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

    book_id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String, nullable=False)
    authors = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    isnb = db.Column(db.String)
    city_published = db.column(db.String)
    edition = db.column(db.Integer)
    publisher = db.Column(db.String)
    copies = db.Column(db.Integer, nullable=False)

    def book_serializer(self):
        """This is a serialized book details stored in dict"""
        book_details = {
            'Book Id': self.book_id,
            'Book Title': self.book_title,
            'Authors': self.authors,
            'Year': self.year,
            'Book edition': self.edition,
            'ISNB': self.isnb,
            'Publisher': self.publisher,
            'City Published': self.city_published,
            'Copies': self.copies
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
