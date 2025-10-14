# python -m pytest tests/R6_test.py

import pytest
from library_service import search_books_in_catalog

def test_search_title_partial_match():
    """Test should return books with titles containing the search."""
    results = search_books_in_catalog("84", "title")

    assert all("84" in book["title"].lower() for book in results)

def test_search_author_partial_match():
    """Test should return books with authors containing the search term."""
    results = search_books_in_catalog("george", "author")

    assert all("george" in book["author"].lower() for book in results)

def test_search_isbn_match():
    """Test should only return book(s) with an exact ISBN match."""
    results = search_books_in_catalog("1234567890123", "isbn")

    assert all(book["isbn"] == "1234567890123" for book in results)

def test_search_isbn_no_match():
    """Test partial ISBN matches must not return results."""
    results = search_books_in_catalog("12345", "isbn")

    assert results == []

def test_search_no_match():
    """Test search with no matches should return an empty list."""
    results = search_books_in_catalog("lololol", "title")

    assert results == []