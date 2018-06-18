from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from sqlalchemy import or_

from app.models import Book, Borrow


def search_book(q):
    """Search for a single in database"""
    if not q or q == "":
        return {"message": "Please specify you query for search."}, 400
    books_found = Book.query.filter(or_(Book.book_title.like('%'+q.title()+'%'), Book.book_isnb.like('%'+q.title()+'%'),
                                        Book.publisher.like('%' + q.title() + '%'), Book.authors.like('%'+q.title()+'%'),
                                        Book.city_published.like('%' + q.title() + '%'))).all()
    if books_found and len(books_found) > 0:
        results = [book.book_serializer() for book in books_found]
        return {"message": "Successfully found books matching {}".format(q),
                "books": results}, 200
    else:
        return {"message": "The books matching {} were not found.".format(q)}, 404


@jwt_required
def user_un_returned_books():
    """Check list of books that user have not returned"""
    return Borrow.query.filter(Borrow.returned == 'false', Borrow.user_id == get_jwt_identity()).all()


