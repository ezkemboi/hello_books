"""
The file contains the for user functions including register, login, logout, reset-password and logout
"""
import json

from tests.BaseTests import HelloBooksTestCase


class AuthTestCase(HelloBooksTestCase):
    """
    Auth test cases for register, login, logout and reset-password
    """

    def test_registration(self):
        """Test user registration"""
        register = self.register()
        self.assertEqual(register.status_code, 201)
        register = self.client.post('/api/v1/auth/register')
        self.assertEqual(register.status_code, 400)

    def test_already_taken_username(self):
        """This tests that username is already taken"""
        self.register()
        second_res = self.register()
        self.assertEqual(second_res.status_code, 409)

    def test_already_registered_user(self):
        """This test code helps to eliminate double registration"""
        self.register()
        second_res = self.client.post('/api/v1/auth/register', data=json.dumps(self.similar_user_email),
                                      content_type='application/json')
        self.assertEqual(second_res.status_code, 422)

    def test_login(self):
        """Test the login for user already registered."""
        self.register()
        login_res = self.login()
        self.assertEqual(login_res.status_code, 200)
        empty_login = self.client.post('/api/v1/auth/login')
        self.assertEqual(empty_login.status_code, 400)
        invalid_login = self.client.post('/api/v1/auth/login', data=json.dumps(self.invalid_user_data),
                                         content_type='application/json')
        self.assertEqual(invalid_login.status_code, 403)

    def test_reset_password(self):
        """"Test reset-password"""
        self.register()
        res = self.client.post('/api/v1/auth/reset-password', data=json.dumps(self.user_data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)

    def test_logout(self):
        """Test"""
        self.authenticate_user()
        logout_user = self.client.post('/api/v1/auth/logout')
        self.assertEqual(logout_user.status_code, 200)
