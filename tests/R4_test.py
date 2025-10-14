# python -m pytest tests/R4_test.py

import pytest
from library_service import return_book_by_patron

VALID_PATRON_ID = "123456"
VALID_BOOK_ID = 1

def test_return_book_success():
    """Test patron returning a borrowed book."""
    success, message = return_book_by_patron(VALID_PATRON_ID, VALID_BOOK_ID)

    assert success == True
    assert "successfully returned" in message.lower()


def test_return_book_not_borrowed():
    """Test patron tries to return a book they didn't borrow."""
    success, message = return_book_by_patron(VALID_PATRON_ID, 67)

    assert success == False
    assert "not borrowed" in message.lower()


def test_return_book_invalid_patron():
    """Test patron ID."""
    success, message = return_book_by_patron("123", VALID_BOOK_ID)

    assert success == False
    assert "invalid patron id" in message.lower()


def test_return_book_updates_copies():
    """Test returning a book should +1 to available copies."""
    success, message = return_book_by_patron(VALID_PATRON_ID, VALID_BOOK_ID)

    assert success == True
    assert "available copies" in message.lower()


def test_return_book_late_fee():
    """Test returning a book past due date with late fees."""
    success, message = return_book_by_patron(VALID_PATRON_ID, VALID_BOOK_ID)

    assert success == True
    assert "late fee" in message.lower()