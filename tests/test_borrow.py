""" This file contains borrow tests such borrow book, return book, borrow history,
un-returned borrowed books"""
import json

from tests.base_tests import HelloBooksTestCase
from run import jwt


class BorrowBooksTestCase(HelloBooksTestCase):
    """This class contains all tests for users"""

    def test_borrow_book(self):
        """Test user borrow book"""
        res = self.borrow_book()
        self.assertEqual(res.status_code, 200)

    def test_borrow_book_already_borrowed(self):
        """Test to borrow a book already borrowed and not yet returned"""
        add_book = self.add_book(self.add_book_data)
        book_data = json.loads(add_book.data)
        login_user = self.login_user(self.user_data)
        login_msg = json.loads(login_user.data)
        access_token = login_msg['access_token']
        self.client.post('/api/v1/users/books/{}'.format(book_data['book_added']['book_id']),
                         headers={"Authorization": "Bearer {}".format(access_token)})
        borrow_again = self.client.post('/api/v1/users/books/{}'.format(book_data['book_added']['book_id']),
                                        headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(borrow_again.status_code, 403)

    def test_return_book(self):
        """Test user returning book"""
        add_book = self.add_book(self.add_book_data)
        book_data = json.loads(add_book.data)
        login_user = self.login_user(self.user_data)
        login_msg = json.loads(login_user.data)
        access_token = login_msg['access_token']
        self.client.post('/api/v1/users/books/{}'.format(book_data['book_added']['book_id']),
                         headers={"Authorization": "Bearer {}".format(access_token)})
        return_book = self.client.put('/api/v1/users/books/{}'.format(book_data['book_added']['book_id']),
                                      headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(return_book.status_code, 200)

    def test_return_unidentified_book(self):
        """Test user returning book"""
        add_book = self.add_book(self.add_book_data)
        book_data = json.loads(add_book.data)
        login_user = self.login_user(self.user_data)
        login_msg = json.loads(login_user.data)
        access_token = login_msg['access_token']
        self.client.post('/api/v1/users/books/{}'.format(book_data['book_added']['book_id']),
                         headers={"Authorization": "Bearer {}".format(access_token)})
        return_un_identified_book = self.client.put('/api/v1/users/books/1342',
                                                    headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(return_un_identified_book.status_code, 400)

    def test_return_borrow_history(self):
        """"Test when user returns history"""
        self.borrow_book()
        login_user = self.login_user(self.user_data)
        login_msg = json.loads(login_user.data)
        access_token = login_msg['access_token']
        res = self.client.get('/api/v1/users/books', headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(res.status_code, 200)

    def test_return_unavailable_borrow(self):
        """Return test for when there is no book borrowed"""
        login_user = self.login_user(self.user_data)
        login_msg = json.loads(login_user.data)
        access_token = login_msg['access_token']
        res = self.client.get('/api/v1/users/books', headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(res.status_code, 404)

    def test_un_returned(self):
        """Tests books user has not returned"""
        self.borrow_book()
        login_user = self.login_user(self.user_data)
        login_msg = json.loads(login_user.data)
        access_token = login_msg['access_token']
        res = self.client.get('/api/v1/users/books?returned=false',
                              headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(res.status_code, 200)

    def test_unavailable_un_returned(self):
        """Tests books user has not returned"""
        login_user = self.login_user(self.user_data)
        login_msg = json.loads(login_user.data)
        access_token = login_msg['access_token']
        res = self.client.get('/api/v1/users/books?returned=false',
                              headers={"Authorization": "Bearer {}".format(access_token)})
        self.assertEqual(res.status_code, 404)
