# python -m pytest tests/R5_test.py

import pytest
from services.library_service import calculate_late_fee_for_book

VALID_PATRON_ID = "123456"
VALID_BOOK_ID = 1

def test_late_fee_not_overdue():
    """Test no fee if book is not overdue."""
    result = calculate_late_fee_for_book(VALID_PATRON_ID, VALID_BOOK_ID)

    assert isinstance(result, dict)
    assert result["days_overdue"] == 0
    assert result["fee_amount"] == 0.00


def test_late_fee_within_7_days():
    """Test $0.50/day fee if overdue <= 7 days."""

    result = calculate_late_fee_for_book(VALID_PATRON_ID, VALID_BOOK_ID)
    assert result["days_overdue"] <= 7
    assert 0 <= result["fee_amount"] <= 3.50


def test_late_fee_after_7_days():
    """Fee increases to $1.00/day after 7 days overdue."""

    result = calculate_late_fee_for_book(VALID_PATRON_ID, VALID_BOOK_ID)
    assert result["days_overdue"] > 7
    assert result["fee_amount"] >= 3.50


def test_late_fee_maximum_cap():
    """Test fee should not exceed $15.00."""

    result = calculate_late_fee_for_book(VALID_PATRON_ID, VALID_BOOK_ID)
    assert result["fee_amount"] <= 15.00


def test_late_fee_response_format():
    """Test response should include fee_amount and days_overdue."""
    result = calculate_late_fee_for_book(VALID_PATRON_ID, VALID_BOOK_ID)

    assert "fee_amount" in result
    assert "days_overdue" in result