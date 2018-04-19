
def test_borrow_unavailable_book(self):
    """Test a user borrowing unavailable book"""
    res = self.client.post('/api/v1/users/books/1267')
    self.assertEqual(res.status_code, 404)
