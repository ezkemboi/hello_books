""" This file contains borrow tests such borrow book, return book, borrow history,
un-returned borrowed books"""
import json

from tests.BaseTests import HelloBooksTestCase


class BorrowBooksTestCase(HelloBooksTestCase):
    """This class contains all tests for users"""

    def borrow_book(self):
        """Reusable borrow book function"""
        self.login()
        response = self.client.post('/api/v1/users/books/1267')
        return response

    def test_borrow_unavailable_book(self):
        """Test a user borrowing unavailable book"""
        self.borrow_book()
        res = self.client.post('/api/v1/users/books/1267')
        self.assertEqual(res.status_code, 404)

    def test_borrow_book(self):
        """Test user borrow book"""
        res = self.borrow_book()
        self.assertEqual(res.status_code, 200)

    def test_return_book(self):
        """Test user returning book"""
        self.borrow_book()
        response = self.client.put('/api/v1/users/books/1267')
        self.assertEqual(response.status_code, 200)
        un_available_book = self.client.put('/api/v1/users/books/1269')
        self.assertEqual(un_available_book.status_code, 400)

    def test_history(self):
        """"Test when user returns history"""
        self.borrow_book()
        res = self.client.get('/api/v1/users/books/')
        self.assertEqual(res.status_code, 200)

    def test_un_returned(self):
        """Tests books user has not returned"""
        self.borrow_book()
        res = self.client.get('/api/v1/users/books/')
        self.assertEqual(res.status_code, 200)
