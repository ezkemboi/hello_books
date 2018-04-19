"""
The file contains tests for books (Adding books, editing, deleting, borrowing and getting
"""
import unittest
import json

import run
from app import create_app
from app.models import db


class UsersTestCase(unittest.TestCase):
    """This class contains all tests for users"""

    def setUp(self):
        """This set environment and initialize application"""
        self.app = create_app(config_name='testing')
        self.client = run.app.test_client()
        self.add_book_data = {
            "book_id": 2345,
            'book_title': 'The Wonder Boy',
            'authors': 'john doe',
            'year': 2006,
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

    def add_book(self):
        """The function help to add book"""
        return self.client.post('/api/v1/books', data=json.dumps(self.add_book_data),
                                content_type='application/json')

    def test_add_book(self):
        """Test that admin should add book"""
        add_book = self.add_book()
        self.assertEqual(add_book.status_code, 201)

    def test_get_all_books(self):
        """Test user can get all books"""
        self.add_book()
        get_all_books = self.client.get('/api/v1/books')
        self.assertEqual(get_all_books.status_code, 200)

    def test_borrow_unavailable_book(self):
        """Test a user borrowing unavailable book"""
        res = self.client.post('/api/v1/users/books/1267')
        self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main()
