"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books,
    get_patron_borrowed_books, get_db_connection  # added two imports for a2
)
def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isbn.isdigit(): # added in a2
        return False, "ISBN must include only digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5: # fixed in a2
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """

    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrowed_book = next((b for b in borrowed_books if b['book_id'] == book_id), None)
    
    if not borrowed_book:
        return False, "This book is not borrowed by this patron."
    
    return_date = datetime.now()
    update_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not update_success:
        return False, "Database error occurred while updating return record."
    
    availability_success = update_book_availability(book_id, +1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    fee_amount = fee_info.get('fee_amount', 0.0)
    days_overdue = fee_info.get('days_overdue', 0)
    status = fee_info.get('status', '')
    
    if days_overdue > 0 and fee_amount > 0:
        message = (
            f'Book: "{book["title"]}" returned successfully. '
            f'Late by: {days_overdue} day(s). Fee: ${fee_amount:.2f}.'
        )
    else:
        message = f'Book: "{book["title"]}" returned successfully. No late fees.'
    
    if status and "not implemented" in status.lower():
        message += f" ({status})"
    
    return True, message

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 
    
    
    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """

    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Invalid patron ID'
        }

    borrowed_books = get_patron_borrowed_books(patron_id)
    borrowed_book = next((b for b in borrowed_books if b['book_id'] == book_id), None)
    
    if not borrowed_book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No active borrow record found (or book already returned)'
        }

    now = datetime.now()
    due_date = borrowed_book['due_date']
    days_overdue = (now.date() - due_date.date()).days

    if days_overdue <= 0:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not overdue'
        }

    if days_overdue <= 7:
        fee = days_overdue * 0.50
    else:
        fee = (7 * 0.50) + ((days_overdue - 7) * 1.00)

    fee = min(fee, 15.00)

    return {
        'fee_amount': round(fee, 2),
        'days_overdue': days_overdue,
        'status': 'Late fee calculated successfully'
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    
    if not search_term or not search_term.strip():
        return []
    
    search_term = search_term.strip()
    search_type = search_type.lower().strip()
    
    valid_types = ['title', 'author', 'isbn']
    if search_type not in valid_types:
        return []
    
    conn = get_db_connection()
    
    try:
        if search_type == 'isbn':
            query = "SELECT * FROM books WHERE isbn = ?"
            params = (search_term,)
        elif search_type == 'title':
            query = "SELECT * FROM books WHERE LOWER(title) LIKE ?"
            params = (f"%{search_term.lower()}%",)
        elif search_type == 'author':
            query = "SELECT * FROM books WHERE LOWER(author) LIKE ?"
            params = (f"%{search_term.lower()}%",)
        
        results = conn.execute(query, params).fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    except Exception as e:
        conn.close()
        return []

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    conn = get_db_connection()
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    total_fees = 0.0
    for book in borrowed_books:
        late_fee_info = calculate_late_fee_for_book(patron_id, book['book_id'])
        total_fees += late_fee_info['fee_amount']
    
    borrowed_count = get_patron_borrow_count(patron_id)
    
    history_rows = conn.execute('''
        SELECT br.*, b.title, b.author
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.patron_id = ?
        ORDER BY br.borrow_date DESC
    ''', (patron_id,)).fetchall()
    
    history = []
    for record in history_rows:
        history.append({
            'book_id': record['book_id'],
            'title': record['title'],
            'author': record['author'],
            'borrow_date': record['borrow_date'],
            'due_date': record['due_date'],
            'return_date': record['return_date']
        })
    
    conn.close()
    
    return {
        'patron_id': patron_id,
        'currently_borrowed': borrowed_books,
        'total_late_fees': round(total_fees, 2),
        'borrowed_count': borrowed_count,
        'borrowing_history': history
    }
