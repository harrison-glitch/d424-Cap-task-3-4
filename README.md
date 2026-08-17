# Restaurant Menu Manager

A full-stack web application built with **Python**, **Flask**, and **SQLite** for managing a restaurant's menu. Built as preparation for the WGU D424 Software Engineering Capstone (Tasks 3 & 4).

---

## Features

- **View** all menu items, filterable by category (Appetizer, Main, Dessert, Drink)
- **Add** new menu items with name, category, description, price, and availability
- **Edit** existing menu items
- **Delete** menu items with confirmation prompt
- **Toggle availability** to mark items on/off the active menu
- **Report page** with summary statistics: total items, availability counts, average/min/max price, and a per-category breakdown

---

## Project Structure

```
restaurant-menu/
├── app.py              # Flask application and all route handlers
├── database.py         # SQLite connection helper and database initialization
├── requirements.txt    # Python dependencies
├── templates/
│   ├── base.html       # Shared layout (nav, flash messages, footer)
│   ├── index.html      # Menu list with filter and action buttons
│   ├── add.html        # Add item form
│   ├── edit.html       # Edit item form
│   └── report.html     # Menu summary report
├── static/
│   └── css/
│       └── style.css   # Application stylesheet
└── tests/
    └── test_app.py     # Pytest test suite (13 tests)
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/d424-cap-task-3-4.git
cd d424-cap-task-3-4

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Then open your browser to: **http://127.0.0.1:5000**

The database is created automatically with sample menu data on first run.

---

## Running Tests

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

All 13 tests should pass covering:
- Page load and category filtering
- Add, edit, delete operations
- Input validation (missing name, invalid price)
- Availability toggling
- Report generation

---

## Routes

| Method | Route           | Description                        |
|--------|-----------------|------------------------------------|
| GET    | `/`             | View all menu items                |
| GET    | `/add`          | Show add item form                 |
| POST   | `/add`          | Submit new menu item               |
| GET    | `/edit/<id>`    | Show edit form for an item         |
| POST   | `/edit/<id>`    | Submit edits for an item           |
| POST   | `/delete/<id>`  | Delete a menu item                 |
| POST   | `/toggle/<id>`  | Toggle item availability           |
| GET    | `/report`       | View menu summary report           |

---

## Tech Stack

- **Backend:** Python 3, Flask 3.0
- **Database:** SQLite (via Python's built-in `sqlite3` module)
- **Frontend:** Jinja2 templates, plain CSS
- **Testing:** pytest

---

## WGU Capstone Notes

This project is designed to satisfy the following D424 Task 3 requirements:

- CRUD functionality (Create, Read, Update, Delete) on menu items
- Report generation feature (the `/report` route)
- Input validation and error handling
- Structured logging throughout the application
- Test suite with documented test criteria

For deployment (Task 4), this application is ready for AWS Elastic Beanstalk. See the deployment section of your capstone documentation for setup steps.
