"""Define all parsers for all classes"""
from flask_restful import reqparse

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', type=str, help='Please enter the email', required=True)
login_parser.add_argument('password', type=str, help='please enter the password', required=True)

register_parser = login_parser.copy()
register_parser.add_argument('username', type=str, help='Please enter your username', required=True)
register_parser.add_argument('first_name', type=str, help='Please enter your first name', required=True)
register_parser.add_argument('last_name', type=str, help='Please enter your last name', required=True)

reset_password_parser = login_parser.copy()

add_book_parser = reqparse.RequestParser()
add_book_parser.add_argument('book_title', type=str, help='Please enter the book title', required=True)
add_book_parser.add_argument('authors', type=str, help='Please enter the authors name', required=True)
add_book_parser.add_argument('year', help='Please enter the year published')
add_book_parser.add_argument('copies', type=int, help='Enter no of copies')
add_book_parser.add_argument('city_published', help="Please enter the city book was published")
add_book_parser.add_argument('book_isnb', type=str, help="Please enter book isnb")
add_book_parser.add_argument('publisher', help="Please enter the book publisher")
add_book_parser.add_argument('edition', type=int, help="Please enter the book edition")

edit_book_parser = add_book_parser.copy()
edit_book_parser.remove_argument('book_title')
edit_book_parser.remove_argument('authors')
edit_book_parser.remove_argument('book_isnb')

get_parser = reqparse.RequestParser()
get_parser.add_argument('page', type=int, help="Please enter an integer as a valid page", location='args')
get_parser.add_argument('limit', type=int, help="Please enter an integer as a valid page limit", location='args')
get_parser.add_argument('q', type=str, help="Please enter search term", location='args')
get_parser.add_argument('returned', type=bool)
