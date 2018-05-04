from app import api

from .user import UserLogin, UserLogout, UserRegistration, ResetPassword
from .book import AddBook, SingleBook
from .borrow import BorrowHistory, BorrowBook

# The registration of all endpoints
api.add_resource(UserRegistration, '/auth/register/')
api.add_resource(UserLogin, '/auth/login/')
api.add_resource(UserLogout, '/auth/logout/')
api.add_resource(ResetPassword, '/auth/reset-password/')

api.add_resource(AddBook, '/books/')
api.add_resource(SingleBook, '/books/<book_id>/')

api.add_resource(BorrowBook, '/users/books/<book_id>/')
api.add_resource(BorrowHistory, '/users/books/')
