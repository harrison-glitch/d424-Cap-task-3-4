"""
database.py - Database initialization and connection helpers for Restaurant Menu Manager.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dict-style access on rows
    return conn


def init_db():
    """Create tables and seed sample data if the database is empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create menu_items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Seed sample data only if table is empty
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_items = [
            ("Mozzarella Sticks", "Appetizer", "Fried mozzarella with marinara sauce", 8.99, 1),
            ("Caesar Salad", "Appetizer", "Romaine, croutons, parmesan, caesar dressing", 9.49, 1),
            ("Cheeseburger", "Main", "8oz beef patty with cheddar, lettuce, tomato", 13.99, 1),
            ("Grilled Salmon", "Main", "Atlantic salmon with lemon butter and vegetables", 18.99, 1),
            ("Margherita Pizza", "Main", "Fresh tomato, mozzarella, and basil", 14.99, 1),
            ("Pasta Carbonara", "Main", "Spaghetti with pancetta, egg, and parmesan", 15.49, 0),
            ("Chocolate Lava Cake", "Dessert", "Warm chocolate cake with vanilla ice cream", 7.99, 1),
            ("Cheesecake", "Dessert", "New York style with strawberry topping", 6.99, 1),
            ("Lemonade", "Drink", "Fresh squeezed lemonade", 3.49, 1),
            ("Iced Tea", "Drink", "House-brewed sweet or unsweet", 2.99, 1),
        ]
        cursor.executemany(
            "INSERT INTO menu_items (name, category, description, price, available) VALUES (?, ?, ?, ?, ?)",
            sample_items
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
