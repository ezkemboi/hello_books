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
        register = self.register_user()
        self.assertEqual(register.status_code, 201)
        empty_registration = self.client.post('/api/v1/auth/register', data=json.dumps(self.empty_data),
                                              content_type='application/json')
        self.assertEqual(empty_registration.status_code, 400)
        invalid_email = self.client.post('/api/v1/auth/register', data=json.dumps(self.invalid_email),
                                         content_type='application/json')
        self.assertEqual(invalid_email.status_code, 400)
        invalid_username = self.client.post('/api/v1/auth/register', data=json.dumps(self.invalid_username),
                                            content_type='application/json')
        self.assertEqual(invalid_username.status_code, 400)
        short_pswd = self.client.post('/api/v1/auth/register', data=json.dumps(self.short_password),
                                      content_type='application/json')
        self.assertEqual(short_pswd.status_code, 400)
        taken_username = self.register_user()
        self.assertEqual(taken_username.status_code, 409)
        similar_email = self.client.post('/api/v1/auth/register', data=json.dumps(self.similar_user_email),
                                         content_type='application/json')
        self.assertEqual(similar_email.status_code, 422)

    def test_login(self):
        """Test user login"""
        self.register_user()
        login_res = self.login_user()
        self.assertEqual(login_res.status_code, 200)
        invalid_login = self.client.post('/api/v1/auth/login', data=json.dumps(self.invalid_user_data),
                                         content_type='application/json')
        self.assertEqual(invalid_login.status_code, 403)

    def test_reset_password(self):
        """"Test user reset-password functionality"""
        self.register_user()
        res = self.client.post('/api/v1/auth/reset-password', data=json.dumps(self.user_data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        wrong_reset_email = self.client.post('/api/v1/auth/reset-password', data=json.dumps(self.user_data_1),
                                             content_type='application/json')
        self.assertEqual(wrong_reset_email.status_code, 404)
        short_reset_psw = self.client.post('/api/v1/auth/reset-password', data=json.dumps(self.short_reset_psw),
                                           content_type='application/json')
        self.assertEqual(short_reset_psw.status_code, 400)

    def test_logout(self):
        """Test logout user functionality"""
        self.register_user()
        login = self.login_user()
        login_msg = json.loads(login.data)
        access_token = login_msg['access_token']
        logout_user = self.client.post('/api/v1/auth/logout',
                                       headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(logout_user.status_code, 200)
        no_token = self.client.post('/api/v1/auth/logout')
        self.assertEqual(no_token.status_code, 401)
