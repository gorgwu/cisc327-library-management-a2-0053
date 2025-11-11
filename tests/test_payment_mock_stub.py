import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

def test_pay_late_fees_success(mocker):
    """Successful payment, should call process_payment() once and return success tuple."""

    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.0})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Mock Book'})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123456_1", "Payment processed successfully")

    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=10.0,
        description="Late fees for 'Mock Book'"
    )
    assert success is True
    assert "Payment successful!" in msg
    assert txn.startswith("txn_")

def test_pay_late_fees_declined(mocker):
    """Payment declined by gateway, should call once and return failure."""

    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.0})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Mock Book'})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Card declined")

    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_called_once()
    assert success is False
    assert "Payment failed" in msg
    assert txn is None

def test_pay_late_fees_invalid_patron(mocker):
    """Invalid patron ID, should not call gateway."""

    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.0})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Mock Book'})

    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn = pay_late_fees("ABC123", 1, mock_gateway)

    mock_gateway.process_payment.assert_not_called()
    assert success is False
    assert "Invalid patron ID" in msg
    assert txn is None

def test_pay_late_fees_zero_fee(mocker):
    """Zero fee, should not call payment gateway."""

    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 0.0})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Mock Book'})

    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_not_called()
    assert success is False
    assert "No late fees" in msg
    assert txn is None

def test_pay_late_fees_network_error(mocker):
    """Network error from gateway, should handle exception gracefully."""

    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 5.0})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Mock Book'})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network failure")

    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_called_once()
    assert success is False
    assert "Payment processing error" in msg
    assert txn is None

def test_refund_success(mocker):
    """Successful refund, should call refund_payment() once and return success."""
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund of $10.00 processed successfully.")

    success, msg = refund_late_fee_payment("txn_123456_1", 10.0, mock_gateway)

    mock_gateway.refund_payment.assert_called_once_with("txn_123456_1", 10.0)
    assert success is True
    assert "Refund" in msg

def test_refund_invalid_transaction_id(mocker):
    """Invalid transaction ID, should not call gateway."""
    mock_gateway = Mock(spec=PaymentGateway)

    success, msg = refund_late_fee_payment("bad_txn", 10.0, mock_gateway)

    mock_gateway.refund_payment.assert_not_called()
    assert success is False
    assert "Invalid transaction ID" in msg

@pytest.mark.parametrize("amount", [-5.0, 0.0, 20.0])
def test_refund_invalid_amounts(mocker, amount):
    """Invalid refund amounts (negative, zero, exceeds limit), should not call gateway."""

    mock_gateway = Mock(spec=PaymentGateway)

    success, msg = refund_late_fee_payment("txn_123456_1", amount, mock_gateway)

    mock_gateway.refund_payment.assert_not_called()
    assert success is False
    assert any(keyword in msg for keyword in [
        "Refund amount must be greater than 0.",
        "Refund amount exceeds maximum late fee."
    ])
