"""
The file contains tests for books (Adding books, editing, deleting, borrowing and getting
"""
import unittest
import os
import json

from app import app, db, api
from app.models import User, Book, Borrow


class UsersTestCase(unittest.TestCase):
    """This class contains all tests for users"""

    def setUp(self):
        """This set environment and initialize application"""
        self.app = app
        self.client = self.app.test_client()
        self.add_book_data = {
            'book_id': "2345",
            'book_title': "The Wonder Boy",
            'authors': "john doe",
            'year': "2006",
        }
        self.edit_book_data = {
            'book_id': "2345",
            'book_title': "The wonder Boy edited version",
            'authors': "john Jack",
            'year': "2007",
        }

        with self.app.app_context():
            # Create all tables
            db.create_all()
            book = Book(book_id="2345", book_title="The wonder Boy edited version",
                        authors="john Jack", year="2007")
            db.session.add(book)
            db.session.commit()

    def tearDown(self):
        """Tear down all initialized variables"""
        with self.app.app_context():
            # Drop all tables
            db.session.remove()
            db.drop_all()
            db.session.commit()

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
        add_book = self.add_book()
        self.assertEqual(add_book.status_code, 201)
        get_all_books = self.client.get('/api/v1/books')
        self.assertEqual(get_all_books.status_code, 200)

    def test_get_single_book(self):
        """Test that a user can get a single book"""
        add_book = self.add_book()
        self.assertEqual(add_book.status_code, 201)
        json_result = json.loads(add_book.data.decode('utf-8').replace("'", "\""))
        result = self.client.get('/api/v1/books{}'.format(json_result['book_id']))
        self.assertEqual(result.status_code, 200)

    def test_can_edit_book(self):
        """Tests that a book can be edited"""
        add_book = self.add_book()
        self.assertEqual(add_book.status_code, 201)
        json_result = json.loads(add_book.data.decode('utf-8').replace("'", "\""))
        edit_book = self.client.put('/api/v1/books/{}'.format(json_result['book_id']),
                                    data=json.dumps(self.edit_book_data), content_type='application/json')
        self.assertEqual(edit_book.status_code, 200)

    def test_book_can_be_deleted(self):
        add_book = self.add_book()
        self.assertEqual(add_book.status_code, 201)
        json_result = json.loads(add_book.data.decode('utf-8').replace("'", "\""))
        delete_book = self.client.delete('/api/v1/books{}'.format(json_result['book_id']))
        self.assertEqual(delete_book.status_code, 204)


if __name__ == '__main__':
    unittest.main()
