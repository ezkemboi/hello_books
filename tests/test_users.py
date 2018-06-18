"""
The file contains the for user functions including register, login, logout, reset-password and logout
"""
import json

from tests.base_tests import HelloBooksTestCase


class AuthTestCase(HelloBooksTestCase):
    """
    Auth test cases for register, login, logout and reset-password
    """

    def test_registration(self):
        """Test user registration"""
        register = self.register_user(self.user_data)
        self.assertEqual(register.status_code, 201)
        empty_registration = self.register_user(self.empty_data)
        self.assertEqual(empty_registration.status_code, 400)
        invalid_email = self.register_user(self.invalid_email)
        self.assertEqual(invalid_email.status_code, 400)
        invalid_username = self.register_user(self.invalid_username)
        self.assertEqual(invalid_username.status_code, 400)
        short_pswd = self.register_user(self.short_password)
        self.assertEqual(short_pswd.status_code, 400)
        similar_email = self.register_user(self.similar_user_email)
        self.assertEqual(similar_email.status_code, 422)
        taken_username = self.register_user(self.similar_username)
        self.assertEqual(taken_username.status_code, 409)

    def test_login(self):
        """Test user login"""
        self.register_user(self.user_data)
        login_res = self.login_user(self.user_data)
        self.assertEqual(login_res.status_code, 200)
        invalid_login = self.login_user(self.invalid_user_data)
        self.assertEqual(invalid_login.status_code, 403)

    def test_reset_password(self):
        """"Test user reset-password functionality"""
        self.register_user(self.user_data)
        res = self.reset_password(self.user_data)
        self.assertEqual(res.status_code, 200)
        wrong_reset_email = self.reset_password(self.user_data_1)
        self.assertEqual(wrong_reset_email.status_code, 404)
        short_reset_psw = self.reset_password(self.short_reset_psw)
        self.assertEqual(short_reset_psw.status_code, 400)

    def test_logout(self):
        """Test logout user functionality"""
        self.register_user(self.user_data)
        login = self.login_user(self.user_data)
        login_msg = json.loads(login.data)
        access_token = login_msg['access_token']
        logout_user = self.client.post('/api/v1/auth/logout',
                                       headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(logout_user.status_code, 200)
        no_token = self.client.post('/api/v1/auth/logout')
        self.assertEqual(no_token.status_code, 401)
