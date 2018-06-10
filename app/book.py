from flask_restful import Resource
from flask_jwt_extended import jwt_required
import random

from app.models import Book, User
from app.parsers import add_book_parser, get_parser, edit_book_parser


def check_admin():
    """Check if user is an admin"""
    return User.query.filter(User.email.endswith('@hellobookslibrary.com')).first()


class AddBook(Resource):
    """
    Contains all the methods to add book, list all books
    """
    @jwt_required
    def post(self):
        """Post method to allow addition of book"""
        args = add_book_parser.parse_args()
        book_title = args['book_title']
        authors = args['authors']
        year = args['year']
        edition = args['edition']
        city_published = args['city_published']
        isnb = args['isnb']
        publisher = args['publisher']
        copies = args['copies']
        admin = check_admin()
        if not admin:
            return {"Message": "Only admin can add a book."}, 403
        check_if_available = Book.query.filter_by(book_title=book_title, authors=authors,
                                                  year=year, edition=edition, city_published=city_published,
                                                  isnb=isnb, publisher=publisher).first()
        if check_if_available is None:
            new_book = Book(book_id=random.randint(1111, 9999), book_title=book_title, authors=authors,
                            year=year, edition=edition, city_published=city_published, isnb=isnb,
                            publisher=publisher, copies=copies)
            new_book.save_book()
            result = new_book.book_serializer()
            return {"Message": "The book was added successfully.", "Book Added": result}, 201
        check_if_available.copies += copies
        check_if_available.update_book()
        return {"Message": "The book exist and was updated", "Details": {
            'book_id': check_if_available.book_id,
            'book_title': check_if_available.book_title,
            'authors': check_if_available.authors,
            'year': check_if_available.year,
            'edition': check_if_available.edition,
            'city_published': check_if_available.city_published,
            'isnb': check_if_available.isnb,
            'publisher': check_if_available.publisher,
            'copies': check_if_available.copies
        }}, 200

    def get(self):
        """Get method to get all books"""
        args = get_parser.parse_args()
        page = args['page']
        limit = args['limit']
        books = Book.query.paginate(page=page, per_page=limit)
        all_books = books.items
        num_results = books.total
        total_pages = books.pages
        current_page = books.page
        has_next_page = books.has_next
        has_prev_page = books.has_prev
        prev_num = books.prev_num
        next_num = books.next_num
        if not all_books:
            return {"Message": "Books not found"}, 404
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
        """Put method to edit already existing book"""
        args = edit_book_parser.parse_args()
        get_book = Book.query.filter_by(book_id=book_id).first()
        book_title = args['book_title']
        authors = args['authors']
        year = args['year']
        edition = args['edition']
        publisher = args['publisher']
        city_published = args['city_published']
        isnb = args['isnb']
        copies = args['copies']
        admin = check_admin()
        if not admin:
            return {"Message": "Only admin can edit a book."}, 403
        if not get_book:
            return {"The book is not found"}, 404
        if get_book:
            get_book.book_title = book_title
            get_book.authors = authors
            get_book.year = year
            get_book.edition = edition
            get_book.publisher = publisher
            get_book.city_published = city_published
            get_book.isnb = isnb
            get_book.copies = copies
            get_book.update_book()
            edited_book = get_book.book_serializer()
            return {"Success": edited_book}, 200

    @jwt_required
    def delete(self, book_id):
        """Delete method to delete a single book"""
        get_book_id = Book.query.filter_by(book_id=book_id).first()
        admin = check_admin()
        if not admin:
            return {"Message": "Admin can only delete a book."}, 403
        if get_book_id:
            get_book_id.delete_book()
            return {"Message": "The book was deleted successfully."}, 204
        return {"Error": "Book not found."}, 404

    def get(self, book_id):
        """Get method for a single book"""
        book = Book.query.filter_by(book_id=book_id).first()
        if book:
            result = book.book_serializer()
            return {"Book": result}, 200
        return {"Error": "Book not found."}, 404