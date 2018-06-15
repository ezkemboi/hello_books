"""This file contains all registered endpoints of the application"""
from app import api

from app.users.views import UserLogin, UserLogout, UserRegistration, ResetPassword
from app.books.views import AddBook, SingleBook
from app.borrow.views import BorrowHistory, BorrowBook

api.add_resource(UserRegistration, '/auth/register/')
api.add_resource(UserLogin, '/auth/login/')
api.add_resource(UserLogout, '/auth/logout/')
api.add_resource(ResetPassword, '/auth/reset-password/')

api.add_resource(AddBook, '/books/')
api.add_resource(SingleBook, '/books/<book_id>/')

api.add_resource(BorrowBook, '/users/books/<book_id>/')
api.add_resource(BorrowHistory, '/users/books/')
