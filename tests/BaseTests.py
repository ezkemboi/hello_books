import unittest
import random
import json

from app import app, db
from app.endpoints import api
from app.models import User, Borrow, Book
from config import app_config


class HelloBooksTestCase(unittest.TestCase):
    """This is the base class for all the tests. It authenticate the user"""
    def setUp(self):
        """It sets up the application and authentication of user"""
        self.app = app
        app.config.from_object(app_config['testing'])
        self.client = self.app.test_client()
        self.user_data = {
            'user_id': random.randint(1111, 9999),
            'email': "myemail@gmail.com",
            'username': "testuser",
            'password': "passwordtrade"
        }
        self.invalid_user_data = {
            'user_id': random.randint(1111, 9999),
            'email': "invalid@email.com",
            'username': "wrongusername",
            'password': "wrongpassword"
        }
        self.similar_user_email = {
            'user_id': random.randint(1111, 9999),
            'email': "myemail@gmail.com",
            'username': "testuser1",
            'password': "passwordtrade"
        }
        self.add_book_data = {
            'book_id': random.randint(1111, 9999),
            'book_title': "The Wonder Boy",
            'authors': "john doe",
            'year': "2006",
        }
        self.edit_book_data = {
            'book_title': "The wonder Boy edited version",
            'authors': "john Jack",
            'year': "2007",
        }

        with self.app.app_context():
            db.create_all()
            user = User(user_id=self.user_data['user_id'], username=self.user_data['username'],
                        email=self.user_data['email'], password=self.user_data['password'])
            book = Book(book_id=self.add_book_data['book_id'], authors=self.add_book_data['authors'],
                        book_title=self.add_book_data['book_title'],
                        year=self.add_book_data['year'])
            db.session.add(user)
            db.session.add(book)
            db.session.commit()

    def tearDown(self):
        """Break all data tables created"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.session.commit()

    def register(self):
        """This method registers a user"""
        return self.client.post('/api/v1/auth/register', data=json.dumps(self.user_data),
                                content_type='application/json')

    def login(self):
        """This is a login user helper"""
        return self.client.post('/api/v1/auth/login', data=json.dumps(self.user_data),
                                content_type='application/json')

    def authenticate_user(self):
        """Authenticate user by generating token"""
        self.register()
        login = self.login()
        token = json.loads(login.data.decode())
        header = {
            'Authorization': token,
            "content_type": "application/json"
        }
        return header

    def add_book(self):
        """This method adds a book"""
        access_token = self.authenticate_user()
        return self.client.post('/api/v1/books', headers=access_token,
                                data=json.dumps(self.add_book_data), content_type='application/json')

if __name__ == '__main__':
    unittest.main()
