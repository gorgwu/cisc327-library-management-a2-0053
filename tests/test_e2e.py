# pytest tests/test_e2e.py

import pytest
from playwright.sync_api import Page, expect

# headless mode
@pytest.fixture(scope="session", autouse=True)
def headless_override(browser_type_launch_args):
    browser_type_launch_args["headless"] = True
    return browser_type_launch_args

BASE_URL = "http://localhost:5000"

def test_add_and_borrow_book(page: Page):

    # Add Book to Catalog
    page.goto(f"{BASE_URL}/add_book")

    page.fill("input[name='title']", "E2E Testing Book")
    page.fill("input[name='author']", "George Wu")
    page.fill("input[name='isbn']", "0162334755690")
    page.fill("input[name='total_copies']", "5")

    page.click("button[type='submit']")

    # Verify Book Added
    page.goto(f"{BASE_URL}/catalog")

    book_row = page.locator("tr", has_text="E2E Testing Book").filter(has_text="0162334755690")
    expect(book_row).to_be_visible()
    
    expect(book_row.get_by_text("E2E Testing Book")).to_be_visible()
    expect(book_row.get_by_text("George Wu")).to_be_visible()
    expect(book_row.get_by_text("0162334755690")).to_be_visible()
    expect(book_row.get_by_text("5/5 Available")).to_be_visible()
    
    expect(book_row.locator("input[name='patron_id']")).to_be_visible()
    expect(book_row.locator("button[type='submit']")).to_be_visible()
    expect(book_row.locator("input[name='book_id']")).to_be_hidden()  # hidden input

    # Borrow the Book
    book_row.locator("input[name='patron_id']").fill("100001")
    
    book_row.locator("button[type='submit']").click()

    # Verify Borrow Success
    flash_success = page.locator(".flash-success")
    expect(flash_success).to_be_visible()
    expect(flash_success).to_contain_text("Successfully borrowed")
    
    expect(book_row.get_by_text("4/5 Available")).to_be_visible()
