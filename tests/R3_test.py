# python -m pytest tests/R3_test.py

import pytest
from services.library_service import borrow_book_by_patron

VALID_PATRON_ID = "123456"
VALID_BOOK_ID = 5
UNAVAILABLE_BOOK_ID = 3

def test_borrow_valid():
    """Test borrowing a book with a valid patron ID and available book."""
    success, message = borrow_book_by_patron(VALID_PATRON_ID, VALID_BOOK_ID)

    assert success == True
    assert "successfully borrowed" in message.lower()

def test_borrow_invalid_patron():
    """Test borrowing a book with an invalid patron ID."""
    invalid_ids = ["", "12345", "abcdef", "1234567"]
    for pid in invalid_ids:
        success, message = borrow_book_by_patron(pid, VALID_BOOK_ID)

        assert success == False
        assert "invalid patron id. must be exactly 6 digits." in message.lower()

def test_borrow_unavailable_book():
    """Test borrowing a book that has zero available copies."""
    success, message = borrow_book_by_patron(VALID_PATRON_ID, UNAVAILABLE_BOOK_ID)

    assert success == False
    assert "this book is currently not available." in message.lower()

def test_borrow_patron_max_books():
    """Borrow a book when patron has reached max limit of 5 books."""
    # needs patron with 5 books borrowed
    success, message = borrow_book_by_patron("222222", VALID_BOOK_ID)

    print("current_borrowed:", 6)  # or check inside function
    print("success:", success)
    print("message:", message)

    assert success == False
    assert "you have reached the maximum borrowing limit of 5 books." in message.lower()
    # this test case will not succeed (unless a patron has 6 books borrowed) since the implementation allows for up to 6 books borrowed, not 5