"""
tests/test_app.py - Unit and integration tests for Restaurant Menu Manager.

Uses a temporary file-based SQLite database (not :memory:) because SQLite
in-memory databases don't persist across separate connections.
"""

import pytest
import sys
import os
import tempfile

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import database


@pytest.fixture
def client():
    """Set up a test Flask client with a temporary file-based database."""
    # Create a temp db file that persists across connections within the test
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    # Point the database module at our temp file
    original_path = database.DB_PATH
    database.DB_PATH = db_path

    # Now import app AFTER patching DB_PATH
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"

    # Initialize schema and seed test data
    conn = database.get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.execute(
        "INSERT INTO menu_items (name, category, description, price, available) VALUES (?, ?, ?, ?, ?)",
        ("Test Burger", "Main", "A test burger", 9.99, 1)
    )
    conn.execute(
        "INSERT INTO menu_items (name, category, description, price, available) VALUES (?, ?, ?, ?, ?)",
        ("Test Salad", "Appetizer", "A test salad", 6.49, 0)
    )
    conn.commit()
    conn.close()

    with flask_app.test_client() as test_client:
        yield test_client

    # Cleanup
    database.DB_PATH = original_path
    os.unlink(db_path)


# --- Index / View Tests ---

def test_index_loads(client):
    """Home page should return 200 and show menu items."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Test Burger" in response.data


def test_index_category_filter(client):
    """Category filter should only show items in the selected category."""
    response = client.get("/?category=Main")
    assert response.status_code == 200
    assert b"Test Burger" in response.data
    assert b"Test Salad" not in response.data


# --- Add Item Tests ---

def test_add_item_get(client):
    """GET /add should return the add form."""
    response = client.get("/add")
    assert response.status_code == 200
    assert b"Add Menu Item" in response.data


def test_add_item_post_valid(client):
    """POST /add with valid data should redirect and show the new item."""
    response = client.post("/add", data={
        "name": "New Pizza",
        "category": "Main",
        "description": "Cheese pizza",
        "price": "11.99",
        "available": "on"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"New Pizza" in response.data


def test_add_item_post_missing_name(client):
    """POST /add with missing name should show validation error."""
    response = client.post("/add", data={
        "name": "",
        "category": "Main",
        "price": "9.99"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Name is required" in response.data


def test_add_item_post_invalid_price(client):
    """POST /add with a non-numeric price should show validation error."""
    response = client.post("/add", data={
        "name": "Bad Item",
        "category": "Main",
        "price": "not-a-price"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"valid number" in response.data


# --- Edit Item Tests ---

def test_edit_item_get(client):
    """GET /edit/<id> should return the edit form pre-filled with item data."""
    response = client.get("/edit/1")
    assert response.status_code == 200
    assert b"Test Burger" in response.data


def test_edit_item_post_valid(client):
    """POST /edit/<id> with valid data should update the item."""
    response = client.post("/edit/1", data={
        "name": "Updated Burger",
        "category": "Main",
        "description": "Updated description",
        "price": "12.99",
        "available": "on"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Updated Burger" in response.data


def test_edit_item_not_found(client):
    """GET /edit/<id> for a nonexistent item should redirect with error."""
    response = client.get("/edit/9999", follow_redirects=True)
    assert response.status_code == 200
    assert b"not found" in response.data


# --- Delete Item Tests ---

def test_delete_item(client):
    """POST /delete/<id> should remove the item and show a success message."""
    response = client.post("/delete/1", follow_redirects=True)
    assert response.status_code == 200
    # Flash message confirms deletion; item should not appear in the table rows
    assert b"deleted" in response.data
    # Test Burger should not appear in table rows (it will appear in flash, so check table section)
    assert b"Test Salad" in response.data  # other item still present
    assert b"A test burger" not in response.data  # description is unique, confirms row removed


def test_delete_nonexistent_item(client):
    """POST /delete/<id> for a nonexistent item should show an error."""
    response = client.post("/delete/9999", follow_redirects=True)
    assert response.status_code == 200
    assert b"not found" in response.data


# --- Toggle Availability Tests ---

def test_toggle_availability(client):
    """POST /toggle/<id> should flip the item's availability status."""
    # Item 1 starts as available — toggling should make it unavailable
    response = client.post("/toggle/1", follow_redirects=True)
    assert response.status_code == 200
    assert b"unavailable" in response.data


# --- Report Tests ---

def test_report_loads(client):
    """GET /report should return 200 and display summary statistics."""
    response = client.get("/report")
    assert response.status_code == 200
    assert b"Menu Report" in response.data
    assert b"Total Items" in response.data
