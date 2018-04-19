"""
The file contains the for user functions including register, login, logout, reset-password and logout
"""
import unittest
import json

from app import create_app
from app.models import db
import run


class AuthTestCase(unittest.TestCase):
    """
    Auth test cases for register, login, logout and reset-password
    """
    def setUp(self):
        """Initialize the application for testing"""
        self.app = create_app(config_name='testing')
        self.client = run.app.test_client()
        self.user_data = {
            'email': "myemail@gmail.com",
            'username': "testuser",
            'password': "passwordtrade"
        }
        self.empty_user_data = {
            'email': "",
            'username': "",
            'password': ""
        }

        with self.app.app_context():
            # Create all tables
            db.create_all()

    def tearDown(self):
        """Tear down all initialized variables"""
        with self.app.app_context():
            # Drop all tables
            db.session.remove()
            db.drop_all()

    def register(self):
        """This method registers a user"""
        return self.client.post('/api/v1/auth/register', data=json.dumps(self.user_data),
                                content_type='application/json')

    def login(self):
        return self.client.post('/api/v1/auth/login', data=json.dumps(self.user_data),
                                content_type='application/json')

    def empty_login(self):
        return self.client.post('/api/v1/auth/login', data=json.dumps(self.empty_user_data),
                                content_type='application/json')

    def test_registration(self):
        """Test user registration"""
        register = self.register()
        self.assertTrue(register, 201)

    def test_empty_registration(self):
        """Test user providing empty data"""
        register = self.client.post('/api/v1/auth/register', data=json.dumps(self.empty_user_data),
                                    content_type='application/json')
        self.assertEqual(register.status_code, 400)

    def test_already_registered(self):
        """This test code helps to eliminate double registration"""
        self.register()
        second_res = self.register()
        self.assertEqual(second_res.status_code, 422)

    def test_login(self):
        """Test the login for user already registered."""
        self.register()
        login_res = self.login()
        self.assertEqual(login_res.status_code, 200)
        self.assertNotEqual(login_res.status_code, 403)

    def test_reset_password(self):
        """"Test reset-password"""
        self.register()
        res = self.client.post('/api/v1/auth/reset-password', data=json.dumps(self.user_data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)

    def test_logout(self):
        """Test for logout already logged in"""
        self.register()
        self.login()
        logout_user = self.client.post('/api/v1/auth/logout', data=json.dumps(self.user_data),
                                       content_type='application/json')
        self.assertEqual(logout_user.status_code, 200)

    def test_empty_login(self):
        self.register()
        empty_login = self.empty_login()
        self.assertEqual(empty_login.status_code, 400)

if __name__ == '__main__':
    unittest.main()
