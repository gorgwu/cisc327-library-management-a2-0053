# python -m pytest tests/R7_test.py

import pytest
from services.library_service import get_patron_status_report

def test_report_currently_borrowed():
    """Test report should include list of currently borrowed books with due dates."""
    report = get_patron_status_report("123456")

    assert "currently_borrowed" in report
    for book in report["currently_borrowed"]:
        assert "title" in book
        assert "due_date" in book

def test_report_total_fees():
    """Test report should include total late fees owed by patron."""
    report = get_patron_status_report("123456")

    assert "total_late_fees" in report
    assert isinstance(report["total_late_fees"], (int, float))

def test_report_books_borrowed_count():
    """Test report should include number of books currently borrowed."""
    report = get_patron_status_report("123456")

    assert "borrowed_count" in report
    assert isinstance(report["borrowed_count"], int)

def test_report_borrowing_history():
    """Test report should include borrowing history."""
    report = get_patron_status_report("123456")

    assert "history" in report
    for book in report["history"]:
        assert "title" in book
        assert "borrow_date" in book
        assert "return_date" in book or "return_date" in book.keys()