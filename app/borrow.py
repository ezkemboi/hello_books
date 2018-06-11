import datetime
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
import random

from app.models import Book, Borrow
from app.parsers import get_parser


@jwt_required
def user_un_returned_books():
    """Check list of books that user have not returned"""
    return Borrow.query.filter(Borrow.returned == 'false',
                               Borrow.user_id == get_jwt_identity()).all()


class BorrowBook(Resource):
    """
    This class hold function for user can borrow, return book and check history
    """
    @jwt_required
    def post(self, book_id):
        """Post method for user to borrow book"""
        available_book = Book.query.filter_by(book_id=book_id).first()
        date_borrowed = datetime.datetime.now()
        due_date = datetime.datetime.now() + datetime.timedelta(days=14)
        if available_book.copies >= 1:
            books_borrowed = user_un_returned_books()
            if len(books_borrowed) > 3:
                return {"Message": "You can borrow only up to 3 books."}, 403
            borrow_book = Borrow(borrow_id=random.randint(1111, 9999),
                                 book_id=book_id, user_id=get_jwt_identity(), returned=False,
                                 date_borrowed=date_borrowed, due_date=due_date)
            available_book.copies -= 1
            borrow_book.save_borrowed_book()
            result = borrow_book.borrow_serializer()
            return {"Book borrowed": result}, 200
        return {"Message": "The book is not available for borrow."}, 404

    @jwt_required
    def put(self, book_id):
        """Put method to allow user return book"""
        return_book = Borrow.query.filter_by(book_id=book_id, returned=False).first()
        if return_book:
            return_book.returned = True
            return_book.return_time = datetime.datetime.now()
            book_in_db = Book.query.filter_by(book_id=book_id).first()
            book_in_db.copies += 1
            return_book.return_borrowed_book()
            return {"Message": "You have returned the book successfully."}, 200
        return {"Message": "Your trying to return unidentified book"}, 400


class BorrowHistory(Resource):
    """
    This class contains the book borrowing history
    """
    @jwt_required
    def get(self):
        """It returns the users borrowing history"""
        args = get_parser.parse_args()
        page = args['page']
        limit = args['limit']
        returned = request.args.get('returned')
        if returned == 'false':
            un_returned_books = user_un_returned_books()
            if not un_returned_books:
                return {"Message": "You do not have books that are un-returned"}, 404
            results = [un_returned_books.borrow_serializer() for un_returned_books in un_returned_books]
            return {"Un_returned books": results}, 200
        else:
            all_borrowed_books = Borrow.query.filter_by(
                user_id=get_jwt_identity()).paginate(
                page=page, per_page=limit)
            all_borrowed = all_borrowed_books.items
            num_results = all_borrowed_books.total
            num_pages = all_borrowed_books.pages
            current_page = all_borrowed_books.page
            has_next_page = all_borrowed_books.has_next
            has_prev_page = all_borrowed_books.has_prev
            prev_num = all_borrowed_books.prev_num
            next_num = all_borrowed_books.next_num
            if len(all_borrowed) < 1:
                return {"Message": "You have not borrowed any book."}, 404
            results = [user_borrows.borrow_serializer()
                       for user_borrows in all_borrowed]
            return {
                "Total results": num_results,
                "Number of pages": num_pages,
                "Current page": current_page,
                "All borrowed books": results,
                "Previous page": prev_num,
                "Next page": next_num
                   }, 200
