from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import random

from app.models import Book, User, Borrow
from app.helpers.parsers import add_book_parser, get_parser, edit_book_parser
from run import jwt


def check_admin():
    """Check if user is an admin"""
    return User.query.filter(User.email.endswith('@hellobookslibrary.com'),
                             User.user_id == get_jwt_identity()).first()


class AddBook(Resource):
    """
    Contains all the methods to add book, list all books
    """
    @jwt_required
    def post(self):
        """Post method to allow addition of book"""
        add_book_args = add_book_parser.parse_args()
        book_title = add_book_args['book_title'].strip().title()
        authors = add_book_args['authors'].strip().title()
        year = add_book_args['year']
        edition = add_book_args['edition']
        city_published = add_book_args['city_published'].strip().title()
        book_isnb = add_book_args['book_isnb']
        publisher = add_book_args['publisher'].strip().title()
        copies = add_book_args['copies']
        available_by_isnb = Book.query.filter_by(book_isnb=book_isnb).first()
        available_by_author_title = Book.query.filter_by(book_title=book_title, authors=authors).first()
        if not check_admin():
            return {"message": "Only admin can add a book."}, 403
        if available_by_isnb:
            return {"message": "This book's id is {}. Please update it.".format(available_by_isnb.book_id)}, 409
        if available_by_author_title:
            return {"message": "This book's is {}. Please update it.".format(available_by_author_title.book_id)}, 409
        new_book = Book(book_id=random.randint(1111, 9999), book_title=book_title, authors=authors,
                        edition=edition, city_published=city_published, book_isnb=book_isnb,
                        publisher=publisher, year=year, copies=copies)
        new_book.save_book()
        return {"message": "The book was added successfully.", "book_added": new_book.book_serializer()}, 201

    def get(self):
        """Get method to get all books"""
        get_books_args = get_parser.parse_args()
        page = get_books_args['page']
        limit = get_books_args['limit']
        books = Book.query.paginate(page=page, per_page=limit)
        all_books = books.items
        num_results = books.total
        total_pages = books.pages
        current_page = books.page
        # if page < 1 or limit < 1 or not page.isdigit() or not page.isdigit():
        #     return {"message": "That is not a valid page number or limit."}, 400
        if current_page == 1:
            has_prev_page = None
        has_next_page = books.has_next
        has_prev_page = books.has_prev
        prev_num = books.prev_num
        next_num = books.next_num
        if not all_books:
            return {"message": "Books not found"}, 404
        results = [book.book_serializer() for book in all_books]
        return {
            "Total results": num_results,
            "Total Pages": total_pages,
            "Current page": current_page,
            "All books": results,
            "Previous page": prev_num,
            "Next page": next_num
               }, 200


class SingleBook(Resource):

    """
    Contains all activities of a single book, including editing, getting and removing a book.
    """
    @jwt_required
    def put(self, book_id):
        """Put method to edit already existing book. Book title, isnb and authors is not edited."""
        edit_book_args = edit_book_parser.parse_args()
        year = edit_book_args['year']
        edition = edit_book_args['edition']
        publisher = edit_book_args['publisher'].strip().title()
        city_published = edit_book_args['city_published'].strip().title()
        copies = edit_book_args['copies']
        get_book = Book.query.filter_by(book_id=book_id).first()
        if get_book:
            if not check_admin():
                return {"message": "Only admin can edit a book."}, 403
            get_book.year = year
            get_book.edition = edition
            get_book.publisher = publisher
            get_book.city_published = city_published
            get_book.copies = copies
            get_book.update_book()
            edited_book = get_book.book_serializer()
            return {"message": "The book was edited successfully.", "details": edited_book}, 200
        return {"The book is not found"}, 404

    @jwt_required
    def delete(self, book_id):
        """Delete method to delete a single book"""
        get_book_id = Book.query.filter_by(book_id=book_id).first()
        is_borrowed = Borrow.query.filter_by(book_id=book_id).first()
        if not check_admin():
            return {"message": "Admin can only delete a book."}, 403
        if get_book_id:
            if is_borrowed:
                return {"message": "This book is currently borrowed and cannot be deleted."}, 403
            get_book_id.delete_book()
            return {"message": "The book was deleted successfully."}, 200
        return {"error": "Book not found."}, 404

    def get(self, book_id):
        """Get method for a single book"""
        book = Book.query.filter_by(book_id=book_id).first()
        if book:
            result = book.book_serializer()
            return {"book_details": result}, 200
        return {"error": "Book not found."}, 404
