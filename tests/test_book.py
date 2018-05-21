"""
The file contains tests for books (Adding books, editing, deleting, borrowing and getting
"""
import json

from tests.BaseTests import HelloBooksTestCase


class BooksTestCase(HelloBooksTestCase):
    """This class contains all tests for users"""

    def register_admin(self):
        """Register admin user to add, edit and delete book"""
        register = self.client.post('/api/v1/auth/register', data=json.dumps(self.admin_data),
                                    content_type='application/json')
        return register

    def login_admin(self):
        """Login registered admin"""
        self.register_admin()
        login = self.client.post('/api/v1/auth/login', data=json.dumps(self.admin_data),
                                 content_type='application/json')
        return login

    def add_book(self):
        """Add book function for reuse"""
        self.login_admin()
        add_book = self.client.post('/api/v1/books', data=json.dumps(self.add_book_data),
                                    content_type='application/json')
        return add_book

    def test_add_book(self):
        """Add book by admin that already exist"""
        add_book = self.add_book()
        self.assertEqual(add_book.status_code, 200)

    def test_add_book_already_exist(self):
        """Add book by admin that already exist"""
        self.add_book()
        add_book = self.client.post('/api/v1/books', data=json.dumps(self.add_book_data),
                                    content_type='application/json')
        self.assertEqual(add_book.status_code, 200)

    def test_add_book_no_token(self):
        """Test that admin can add a book"""
        self.login_admin()
        add_book = self.client.post('/api/v1/books', data=json.dumps(self.edit_book_data),
                                    content_type='application/json')
        self.assertEqual(add_book.status_code, 401)

    def test_add_book_missing_all_details(self):
        """Test that admin should add book"""
        self.register()
        self.login()
        add_book = self.client.post('/api/v1/books', data=self.missing_book_data, content_type='application/json')
        self.assertEqual(add_book.status_code, 400)

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

    def test_can_edit_book_no_token(self):
        """Tests that a book can be edited"""
        self.login_admin()
        edit_book = self.client.put('/api/v1/books/8956', data=json.dumps(self.edit_book_data),
                                    content_type='application/json')
        self.assertEqual(edit_book.status_code, 401)

    def test_book_can_be_deleted_no_token(self):
        delete_book = self.client.delete('/api/v1/books/9056')
        self.assertEqual(delete_book.status_code, 401)

    def test_book_can_be_deleted(self):
        add_book = self.add_book()
        self.assertEqual(add_book.status_code, 201)
        json_result = json.loads(add_book.data.decode('utf-8').replace("'", "\""))
        delete_book = self.client.delete('/api/v1/books{}'.format(json_result['book_id']))
        self.assertEqual(delete_book.status_code, 204)
