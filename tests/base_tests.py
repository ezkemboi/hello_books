import unittest
import random
import json

from app import app, db
from config import app_config
from app.helpers import endpoints
from run import jwt


class HelloBooksTestCase(unittest.TestCase):
    """This is the base class for all the tests. It authenticate the user"""
    def setUp(self):
        """It sets up the application and authentication of user"""
        self.app = app
        app.config.from_object(app_config['testing'])
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user_data = {
            'user_id': random.randint(1111, 9999),
            'email': "user@gmail.com",
            'username': "user",
            'first_name': "John",
            'last_name': "Doe",
            'password': "password"
        }
        self.admin_data = {
            'user_id': random.randint(1111, 9999),
            'email': "admin@hellobookslibrary.com",
            'first_name': "Admin",
            'last_name': "Clarke",
            'username': "admin",
            'password': "adminpassword"
        }
        self.short_reset_psw = {
            'email': "user@gmail.com",
            'password': "short"
        }
        self.empty_email_on_reset = {
            'user_id': random.randint(1111, 9999),
            'email': "",
            'username': "testuser",
            'first_name': "Clarke",
            'last_name': "Mike",
            'password': "validpassword"
        }
        self.user_data_1 = {
            'user_id': random.randint(1111, 9999),
            'username': 'user1',
            'email': 'user1@gmail.com',
            'first_name': "Clarke",
            'last_name': "Mike",
            'password': 'user1password'
        }
        self.empty_data = {
            'user_id': random.randint(1111, 9999),
            'username': '',
            'email': '',
            'password': '',
            'first_name': '',
            'last_name': ''
        }
        self.invalid_email = {
            'user_id': random.randint(1111, 9999),
            'username': 'johndoe',
            'email': 'invalid@email',
            'first_name': "Clarke",
            'last_name': "Mike",
            'password': 'password'
        }
        self.invalid_username = {
            'user_id': random.randint(1111, 9999),
            'username': 'use',
            'email': 'user1@gmail.com',
            'first_name': "Clarke",
            'last_name': "Mike",
            'password': 'user1password'
        }
        self.short_password = {
            'user_id': random.randint(1111, 9999),
            'username': 'user2',
            'email': 'user2@gmail.com',
            'first_name': "Clarke",
            'last_name': "Mike",
            'password': 'user1'
        }
        self.invalid_user_data = {
            'user_id': random.randint(1111, 9999),
            'email': "invalid@email.com",
            'username': "wrongusername",
            'first_name': "wrongClarke",
            'last_name': "wrongMike",
            'password': "wrongpassword"
        }
        self.similar_user_email = {
            'user_id': random.randint(1111, 9999),
            'email': "user@gmail.com",
            'username': "testkk",
            'first_name': "Clarke",
            'last_name': "Mike",
            'password': "passwordtrade"
        }
        self.similar_username = {
            'user_id': random.randint(1111, 9999),
            'email': "jkcharles@gmail.com",
            'username': "user",
            'first_name': "Clarke",
            'last_name': "Mike",
            'password': "passwordtrade"
        }
        self.add_book_data = {
            'book_id': random.randint(1111, 9999),
            'book_title': "The Wonder Boy",
            'authors': "john doe",
            'year': "2006",
            'edition': '1',
            'city_published': "Nairobi",
            'book_isnb': "2783722982",
            'publisher': "Longhorn",
            'copies': "2"
        }
        self.similar_book_data = {
            'book_title': "The Wonder Boy",
            'authors': "john doe",
            'year': "2006",
            'edition': '1',
            'city_published': "Nairobi",
            'book_isnb': "27837982",
            'publisher': "Longhorn",
            'copies': "2"
        }
        self.edit_book_data = {
            'book_title': "The wonder Boy edited version",
            'authors': "john Jack",
            'year': "2007",
            'book_isnb': "2783722982",
            'publisher': "Longhorn",
            'city_published': "Nairobi",
            'edition': '1',
            'copies': "12"
        }
        self.missing_book_data = {
            'book_id': random.randint(1111, 9999),
            'book_title': "",
            'authors': "",
            'year': "2006",
            'copies': "2"
        }

    def tearDown(self):
        """Break all data tables created"""
        db.session.close()
        db.drop_all()
        self.app_context.pop()

    def register_user(self, data):
        """This method registers a user"""
        return self.client.post('/api/v1/auth/register', data=json.dumps(data),
                                content_type='application/json')

    def login_user(self, data):
        """This is a login user helper"""
        self.register_user(self.user_data)
        return self.client.post('/api/v1/auth/login', data=json.dumps(data),
                                content_type='application/json')

    def register_admin(self, data):
        """This method register admin"""
        return self.client.post('/api/v1/auth/register', data=json.dumps(data),
                                content_type='application/json')

    def login_admin(self, data):
        """Register and login admin"""
        self.register_admin(self.admin_data)
        return self.client.post('/api/v1/auth/login', data=json.dumps(data),
                                content_type='application/json')

    def reset_password(self, data):
        return self.client.post('/api/v1/auth/reset-password', data=json.dumps(data),
                                content_type='application/json')

    def add_book(self, data):
        """Add book function for reuse"""
        admin_login = self.login_admin(self.admin_data)
        login_msg = json.loads(admin_login.data)
        access_token = login_msg['access_token']
        add_book = self.client.post('/api/v1/books', data=json.dumps(data),
                                    headers={
                                             "Authorization": "Bearer {}".format(access_token)},
                                    content_type='application/json')
        return add_book

    def borrow_book(self):
        """Reusable borrow book function"""
        add_book = self.add_book(self.add_book_data)
        book_data = json.loads(add_book.data)
        login_user = self.login_user(self.user_data)
        login_msg = json.loads(login_user.data)
        access_token = login_msg['access_token']
        user_borrow_book = self.client.post('/api/v1/users/books/{}'.format(book_data['book_added']['book_id']),
                                            headers={"Authorization": "Bearer {}".format(access_token)})
        return user_borrow_book


if __name__ == '__main__':
    unittest.main()
