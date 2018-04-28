"""
The file contains tests for books (Adding books, editing, deleting, borrowing and getting
"""
import json

from tests.BaseTests import HelloBooksTestCase


class BooksTestCase(HelloBooksTestCase):
    """This class contains all tests for users"""

    # def test_add_book(self):
    #     """Test that admin should add book"""
    #     self.authenticate_user()
    #     add_book = self.add_book()
    #     self.assertEqual(add_book.status_code, 201)

    def test_get_all_books(self):
        """Test user can get all books"""
        get_all_books = self.client.get('/api/v1/books')
        self.assertEqual(get_all_books.status_code, 200)

    def test_get_single_book(self):
        """Test that a user can get a single book"""
        book = self.add_book_data['book_id']
        result = self.client.get('/api/v1/books/{}'.format(book))
        self.assertEqual(result.status_code, 200)
        result2 = self.client.get('/api/v1/books/1234')
        self.assertEqual(result2.status_code, 404)

    # def test_can_edit_book(self):
    #     """Tests that a book can be edited"""
    #     add_book = self.add_book()
    #     self.assertEqual(add_book.status_code, 201)
    #     json_result = json.loads(add_book.data.decode('utf-8').replace("'", "\""))
    #     edit_book = self.client.put('/api/v1/books/{}'.format(json_result['book_id']),
    #                                 data=json.dumps(self.edit_book_data), content_type='application/json')
    #     self.assertEqual(edit_book.status_code, 200)
    #
    # def test_book_can_be_deleted(self):
    #     add_book = self.add_book()
    #     self.assertEqual(add_book.status_code, 201)
    #     json_result = json.loads(add_book.data.decode('utf-8').replace("'", "\""))
    #     delete_book = self.client.delete('/api/v1/books{}'.format(json_result['book_id']))
    #     self.assertEqual(delete_book.status_code, 204)

