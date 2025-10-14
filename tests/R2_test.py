# python -m pytest tests/R2_test.py

import pytest
from library_service import get_all_books, add_book_to_catalog

def test_catalog_returns_books():
    """Test that get_all_books() returns all books in the catalog."""
    
    success, message = add_book_to_catalog("Test Book", "Test Author", "9999999999999", 5)

    assert success, "failed to add book for catalog test"
    
    books = get_all_books()
    
    assert isinstance(books, list)
    assert len(books) > 0
    
    test_book = next((b for b in books if b['isbn'] == "9999999999999"), None)
    assert test_book is not None, "Test book not found in catalog"
    
    assert 'id' in test_book
    assert 'title' in test_book
    assert 'author' in test_book
    assert 'isbn' in test_book
    assert 'available_copies' in test_book
    assert 'total_copies' in test_book