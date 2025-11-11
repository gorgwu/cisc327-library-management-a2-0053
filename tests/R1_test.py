# python -m pytest tests/R1_test.py

import pytest
from services.library_service import add_book_to_catalog

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890128", 5)

    assert success == True
    assert "successfully added" in message.lower()


def test_add_book_no_title():
    """Test adding a book with no title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)

    assert success == False
    assert "title is required." in message.lower()


def test_add_book_long_title():
    """Test adding a book with title over 200 chars."""
    long_title = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbbbbbbaaaaaaaaaaaaaaaaaaccaa"
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890123", 5)

    assert success == False
    assert "title must be less than 200 characters." in message.lower()


def test_add_book_no_author():
    """Test adding a book with no author."""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)

    assert success == False
    assert "author is required." in message.lower()


def test_add_book_author_too_long():
    """Test adding a book with author over 100 chars."""
    long_author = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbbbbbbaaaaaaaaaaaaaaaaaaccaa"
    success, message = add_book_to_catalog("Test Book", long_author, "1234567890123", 5)

    assert success == False
    assert "author must be less than 100 characters." in message.lower()


def test_add_book_invalid_isbn_length():
    """Test adding a book with ISBN not equal to 13 digits."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)

    assert success == False
    assert "isbn must be exactly 13 digits." in message.lower()

def test_add_book_invalid_isbn_nondigits():
    """Test adding a book with ISBN containing non-digit chars."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "A1234567890BB", 5)

    assert success == False
    assert "isbn must have only digits" in message.lower()
    # this test case should never succeed since the implementation does not check for this, so a book will be added


def test_add_book_invalid_total_copies():
    """Test adding a book with negative copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -5)

    assert success == False
    assert "total copies must be a positive integer." in message.lower()


def test_add_book_duplicate_isbn():
    """test adding a book with a duplicate ISBN."""
    success, message = add_book_to_catalog("1984", "George Orwell", "9780451524935", 5)

    assert success == False
    assert "a book with this isbn already exists." in message.lower()