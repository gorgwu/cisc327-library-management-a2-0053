import pytest
from datetime import datetime
from unittest.mock import patch
from services.library_service import return_book_by_patron
from services.payment_service import PaymentGateway

# PaymentGateway (from payment_service.py)

def test_process_payment_success():
    """Valid payment should succeed."""
    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("123456", 10.0, "Late fee")
    assert success is True
    assert txn_id.startswith("txn_")
    assert "Payment of $10.00 processed successfully" in msg


def test_process_payment_invalid_amount_zero():
    """Fails when amount is zero."""
    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("123456", 0)
    assert not success
    assert "invalid amount" in msg.lower()


def test_process_payment_negative_amount():
    """Fails when amount is negative."""
    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("123456", -5)
    assert not success
    assert "invalid amount" in msg.lower()


def test_process_payment_exceeds_limit():
    """Fails when amount exceeds 1000."""
    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("123456", 2000)
    assert not success
    assert "declined" in msg.lower()


def test_process_payment_invalid_patron_id():
    """Fails when patron ID is not 6 digits."""
    gateway = PaymentGateway()
    success, txn_id, msg = gateway.process_payment("1234", 10)
    assert not success
    assert "invalid patron id" in msg.lower()


def test_refund_payment_success():
    """Valid refund should succeed."""
    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("txn_123456_1234", 5.0)
    assert success
    assert "refund of $5.00 processed successfully" in msg.lower()


def test_refund_payment_invalid_txn():
    """Invalid transaction ID."""
    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("bad_txn", 5)
    assert not success
    assert "invalid transaction id" in msg.lower()


def test_refund_payment_invalid_amount():
    """Refund with invalid (zero) amount."""
    gateway = PaymentGateway()
    success, msg = gateway.refund_payment("txn_123456_123", 0)
    assert not success
    assert "invalid refund amount" in msg.lower()


def test_verify_payment_status_valid():
    """Should return completed status for valid txn ID."""
    gateway = PaymentGateway()
    result = gateway.verify_payment_status("txn_123456_999")
    assert result["status"] == "completed"
    assert "timestamp" in result


def test_verify_payment_status_invalid():
    """Should return not_found for invalid txn ID."""
    gateway = PaymentGateway()
    result = gateway.verify_payment_status("invalid_txn")
    assert result["status"] == "not_found"
    assert "transaction not found" in result["message"].lower()

# return_book_by_patron (from library_service.py)

@patch("services.library_service.get_book_by_id")
def test_return_book_not_found(mock_get_book):
    """Book not found."""
    mock_get_book.return_value = None
    success, msg = return_book_by_patron("123456", 1)
    assert not success
    assert "book not found" in msg.lower()


@patch("services.library_service.get_book_by_id")
@patch("services.library_service.get_patron_borrowed_books")
def test_return_book_not_in_borrowed(mock_borrowed, mock_book):
    """Patron did not borrow the book."""
    mock_book.return_value = {"id": 1, "title": "Mock"}
    mock_borrowed.return_value = []
    success, msg = return_book_by_patron("123456", 1)
    assert not success
    assert "not borrowed" in msg.lower()


@patch("services.library_service.update_borrow_record_return_date")
@patch("services.library_service.get_patron_borrowed_books")
@patch("services.library_service.get_book_by_id")
def test_return_book_db_error_update(mock_book, mock_borrowed, mock_update):
    """Simulate DB error updating return date."""
    mock_book.return_value = {"id": 1, "title": "Mock"}
    mock_borrowed.return_value = [{"book_id": 1}]
    mock_update.return_value = False
    success, msg = return_book_by_patron("123456", 1)
    assert not success
    assert "database error" in msg.lower()


@patch("services.library_service.update_book_availability")
@patch("services.library_service.update_borrow_record_return_date")
@patch("services.library_service.get_patron_borrowed_books")
@patch("services.library_service.get_book_by_id")
def test_return_book_db_error_availability(mock_book, mock_borrowed, mock_update, mock_avail):
    """Simulate DB error on availability update."""
    mock_book.return_value = {"id": 1, "title": "Mock"}
    mock_borrowed.return_value = [{"book_id": 1}]
    mock_update.return_value = True
    mock_avail.return_value = False
    success, msg = return_book_by_patron("123456", 1)
    assert not success
    assert "database error" in msg.lower()


@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.update_book_availability")
@patch("services.library_service.update_borrow_record_return_date")
@patch("services.library_service.get_patron_borrowed_books")
@patch("services.library_service.get_book_by_id")
def test_return_book_with_late_fee(mock_book, mock_borrowed, mock_update, mock_avail, mock_fee):
    """Return successful with late fee applied."""
    mock_book.return_value = {"id": 1, "title": "Mock"}
    mock_borrowed.return_value = [{"book_id": 1}]
    mock_update.return_value = True
    mock_avail.return_value = True
    mock_fee.return_value = {"fee_amount": 5.0, "days_overdue": 2, "status": "Late fee calculated successfully"}

    success, msg = return_book_by_patron("123456", 1)
    assert success
    assert "late by: 2 day(s)" in msg.lower()
    assert "$5.00" in msg


@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.update_book_availability")
@patch("services.library_service.update_borrow_record_return_date")
@patch("services.library_service.get_patron_borrowed_books")
@patch("services.library_service.get_book_by_id")
def test_return_book_no_late_fee(mock_book, mock_borrowed, mock_update, mock_avail, mock_fee):
    """Return successful with no late fees."""
    mock_book.return_value = {"id": 1, "title": "Mock"}
    mock_borrowed.return_value = [{"book_id": 1}]
    mock_update.return_value = True
    mock_avail.return_value = True
    mock_fee.return_value = {"fee_amount": 0.0, "days_overdue": 0, "status": "Book not overdue"}

    success, msg = return_book_by_patron("123456", 1)
    assert success
    assert "no late fees" in msg.lower()


@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.update_book_availability")
@patch("services.library_service.update_borrow_record_return_date")
@patch("services.library_service.get_patron_borrowed_books")
@patch("services.library_service.get_book_by_id")
def test_return_book_status_not_implemented(mock_book, mock_borrowed, mock_update, mock_avail, mock_fee):
    """Covers 'not implemented' message branch."""
    mock_book.return_value = {"id": 1, "title": "Mock"}
    mock_borrowed.return_value = [{"book_id": 1}]
    mock_update.return_value = True
    mock_avail.return_value = True
    mock_fee.return_value = {"fee_amount": 0.0, "days_overdue": 0, "status": "Late fee calculation not implemented"}

    success, msg = return_book_by_patron("123456", 1)
    assert success
    assert "not implemented" in msg.lower()


def test_return_book_invalid_patron_id():
    """Invalid patron ID should fail immediately."""
    success, msg = return_book_by_patron("12", 1)
    assert not success
    assert "invalid patron id" in msg.lower()
