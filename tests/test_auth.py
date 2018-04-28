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
        register = self.client.post('/api/v1/auth/register', data=json.dumps(self.user_data_1),
                                    content_type='application/json')
        self.assertEqual(register.status_code, 201)
        empty_registration = self.client.post('/api/v1/auth/register', data=json.dumps(self.empty_data),
                                              content_type='application/json')
        self.assertEqual(empty_registration.status_code, 400)

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
        invalid_login = self.client.post('/api/v1/auth/login', data=json.dumps(self.invalid_user_data),
                                         content_type='application/json')
        self.assertEqual(invalid_login.status_code, 403)
        empty_login_data = self.client.post('/api/v1/auth/login', data=json.dumps(self.empty_data),
                                            content_type='application/json')
        self.assertEqual(empty_login_data.status_code, 400)

    def test_reset_password(self):
        """"Test reset-password"""
        self.register()
        res = self.client.post('/api/v1/auth/reset-password', data=json.dumps(self.user_data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        wrong_reset_email = self.client.post('/api/v1/auth/reset-password', data=json.dumps(self.user_data_1),
                                             content_type='application/json')
        self.assertEqual(wrong_reset_email.status_code, 404)
        short_reset_psw = self.client.post('/api/v1/auth/reset-password', data=json.dumps(self.short_reset_psw),
                                           content_type='application/json')
        self.assertEqual(short_reset_psw.status_code, 400)

    def test_invalid_email_on_register(self):
        """Test user providing an invalid email"""
        register = self.client.post('/api/v1/auth/register', data=json.dumps(self.invalid_email),
                                    content_type='application/json')
        self.assertEqual(register.status_code, 400)

    def test_invalid_username_on_register(self):
        """Test user providing short username"""
        register = self.client.post('/api/v1/auth/register', data=json.dumps(self.invalid_username),
                                    content_type='application/json')
        self.assertEqual(register.status_code, 400)

    def test_short_password_on_register(self):
        """Test short password"""
        register = self.client.post('/api/v1/auth/register', data=json.dumps(self.short_password),
                                    content_type='application/json')
        self.assertEqual(register.status_code, 400)

    # def test_logout(self):
    #     """Test"""
    #     logout_user = self.client.post('/api/v1/auth/logout', {'Authorization': 'Bearer ' +
    #                                                                             self.authenticate_user(), },
    #                                    content_type='application/json')
    #     res = json.loads(logout_user.data.decode())
    #     self.assertEqual(logout_user.status_code, 200)
