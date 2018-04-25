from app import api
from .app import UserLogin, UserLogout, UserRegistration, ResetPassword, AddBook, SingleBook, BorrowBook, \
    BorrowHistory, UnReturnedBooks

# The registration of all endpoints
api.add_resource(UserRegistration, '/auth/register/')
api.add_resource(UserLogin, '/auth/login/')
api.add_resource(UserLogout, '/auth/logout/')
api.add_resource(ResetPassword, '/auth/reset-password/')

api.add_resource(AddBook, '/books/')
api.add_resource(SingleBook, '/books/<book_id>/')

api.add_resource(BorrowBook, '/users/books/<book_id>/')
api.add_resource(BorrowHistory, '/users/books/')
api.add_resource(UnReturnedBooks, '/users/books?returned=false')
