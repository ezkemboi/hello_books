# """ This file contains borrow tests such borrow book, return book, borrow history,
# un-returned borrowed books"""
# # import json
#
# from tests.BaseTests import HelloBooksTestCase
#
#
# class BorrowBooksTestCase(HelloBooksTestCase):
#     """This class contains all tests for users"""
#
#     def test_borrow_unavailable_book(self):
#         """Test a user borrowing unavailable book"""
#         res = self.client.post('/api/v1/users/books/1267')
#         self.assertEqual(res.status_code, 404)
