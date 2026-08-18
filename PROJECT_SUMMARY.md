# Restaurant Menu Manager — Project Summary

---

## Overview

This project is a web-based menu management application built using Python, Flask, and SQLite. The application allows a user to create, read, update, and delete restaurant menu items through a browser interface, toggle item availability, and generate a summary report of the menu.

---

## Languages and Tools Used

| Tool | Purpose |
|------|---------|
| Python | Primary programming language |
| Flask | Web framework — handles routing, requests, and templates |
| SQLite | Database — built into Python, no separate setup required |
| Jinja2 | HTML templating engine — bundled with Flask |
| CSS | Frontend styling |
| pytest | Automated testing framework |
| Git | Version control |
| GitHub | Remote code repository |

---

## The 12 Steps

---

### Step 1 — Create the Project Folder

The project was initialized using the macOS Terminal. A root directory named `restaurant-menu` was created on the Desktop using the `mkdir` command. The working directory was then changed into that folder using `cd`. Three subdirectories were created inside it: `templates`, `static/css`, and `tests`.

The `templates` directory is required by Flask. When `render_template()` is called in a route, Flask searches for the specified HTML file inside a folder named exactly `templates` in the same directory as the application file. The `static/css` directory is where Flask serves non-Python files such as stylesheets and images. The `tests` directory holds the pytest test suite and is kept separate from application code as a standard convention.

The `mkdir -p static/css` command uses the `-p` flag, which instructs the system to create all intermediate directories in the path simultaneously, producing both `static/` and `css/` inside it in a single command rather than two separate ones.

---

### Step 2 — Python Virtual Environment

A Python virtual environment was created in the project root using the command `python3 -m venv venv`. This command invokes Python's built-in `venv` module and creates a self-contained directory also named `venv` that holds its own Python interpreter and package installation location.

The virtual environment was then activated using `source venv/bin/activate`. Upon activation, the terminal prompt updates to display `(venv)` as a prefix, confirming that all subsequent Python and pip commands operate within this isolated environment rather than the system-wide Python installation.

The purpose of this isolation is to prevent version conflicts between projects. Without a virtual environment, all Python projects on a machine share the same package versions. If two projects require different versions of the same package, one will always break. Virtual environments eliminate this problem entirely. It is standard practice to create one per project and to never commit the `venv` directory to version control.

---

### Step 3 — Dependencies and requirements.txt

A file named `requirements.txt` was created in the project root. This file lists the external Python packages the project depends on, with each package pinned to a specific version using the `==` operator:

```
Flask==3.0.3
pytest==8.3.2
```

The packages were installed by running `pip install -r requirements.txt`. The `-r` flag instructs pip to read the file and install every package listed within it.

Flask version 3.0.3 is the web framework that provides the server, routing system, request handling, templating engine, and session management used throughout the application. Pytest version 8.3.2 is the testing framework used to write and run the automated test suite.

Pinning exact versions rather than using open ranges such as `Flask>=3.0` ensures that the environment is fully reproducible. Any developer who clones the repository and runs `pip install -r requirements.txt` will receive the identical package versions used during development, eliminating discrepancies caused by newer releases introducing breaking changes.

---

### Step 4 — database.py

A file named `database.py` was created in the project root. This file is responsible for all database configuration, connection management, schema creation, and initial data seeding. It contains three components: a path constant, a connection function, and an initialization function.

**The database path constant:**

```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")
```

`DB_PATH` holds the absolute file path to the SQLite database file. `__file__` is a Python built-in that contains the full path of the current module. `os.path.dirname()` extracts the directory portion of that path, removing the filename. `os.path.join()` appends `menu.db` to produce a complete absolute path. This approach is used rather than a relative path such as `"menu.db"` because a relative path resolves based on whatever directory the terminal is in when the application is launched, which may not be the project root. The absolute path constructed from `__file__` is always correct regardless of where the application is executed from.

**The connection function:**

```python
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

`sqlite3.connect(DB_PATH)` opens the database file and returns a connection object. If the file does not yet exist, SQLite creates it automatically. The line `conn.row_factory = sqlite3.Row` modifies how fetched rows are returned. Without this setting, rows come back as plain tuples and data must be accessed by integer index, for example `row[0]` or `row[2]`. With `sqlite3.Row` set as the row factory, rows behave like dictionaries and data is accessed by column name, for example `row["name"]` or `row["price"]`. This makes the application code significantly more readable and less fragile to changes in column order.

**The initialization function:**

```python
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

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
```

`init_db()` creates the database schema and seeds initial data. The `CREATE TABLE IF NOT EXISTS` clause ensures the table is only created if it does not already exist, making this function safe to call every time the application starts without risk of overwriting stored data.

The table schema defines six columns. `id` is an auto-incrementing integer that serves as the primary key — SQLite assigns this value automatically and it is never set manually. `name` and `category` are text fields marked `NOT NULL`, meaning the database will reject any row that omits them. `description` has no `NOT NULL` constraint, making it optional. `price` is stored as `REAL`, SQLite's type for floating-point decimal numbers. `available` is stored as `INTEGER` with a default value of `1` because SQLite has no native boolean type. The convention `1` represents true and `0` represents false.

After creating the table, the function checks whether it is empty and inserts ten sample rows if so, using `cursor.executemany()` with parameterized queries. The `?` placeholders in the SQL string are a security requirement. Placing variables directly into SQL strings using string formatting would expose the application to SQL injection attacks, where a malicious user could type SQL code into a form field and manipulate or destroy the database. Parameterized queries pass values to the database engine separately, where they are treated strictly as data and never interpreted as SQL commands.

The function concludes with `conn.commit()` to persist all changes to disk and `conn.close()` to release the connection resource.

---

### Step 5 — app.py

A file named `app.py` was created in the project root. This is the application's entry point and contains all route definitions, request handling logic, input validation, and database interaction for the web interface.

**Application setup:**

```python
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = "restaurant-menu-secret-key"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

CATEGORIES = ["Appetizer", "Main", "Dessert", "Drink"]
```

`Flask(__name__)` creates the application instance. The `__name__` argument tells Flask to locate the `templates` and `static` directories relative to the current file. `app.secret_key` is required by Flask to cryptographically sign the session cookie that stores flash messages between requests. Logging is configured to include a timestamp and severity level on every log line. `CATEGORIES` is defined once at the module level so it is referenced from a single location throughout all routes and templates.

**The index route:**

```python
@app.route("/")
def index():
    category_filter = request.args.get("category", "")
    try:
        conn = get_connection()
        if category_filter:
            items = conn.execute(
                "SELECT * FROM menu_items WHERE category = ? ORDER BY category, name",
                (category_filter,)
            ).fetchall()
        else:
            items = conn.execute(
                "SELECT * FROM menu_items ORDER BY category, name"
            ).fetchall()
        conn.close()
        logger.info("Loaded %d menu items (filter: '%s')", len(items), category_filter)
    except Exception as e:
        logger.error("Failed to load menu items: %s", e)
        flash("Error loading menu items.", "danger")
        items = []

    return render_template("index.html", items=items,
                           categories=CATEGORIES, selected_category=category_filter)
```

The `@app.route("/")` decorator registers this function as the handler for the root URL. `request.args.get("category", "")` reads an optional query parameter from the URL. When a user clicks the Main filter button, the browser navigates to `/?category=Main`, and this call retrieves the value `"Main"`. The empty string is the default when no filter is present. All database operations are wrapped in `try/except` so that any error is caught, logged, and communicated to the user with a flash message rather than an unhandled exception. `render_template` loads the specified HTML file and makes the Python variables available inside it.

**The add route:**

```python
@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()
        available = 1 if request.form.get("available") else 0
        ...
    return render_template("add.html", categories=CATEGORIES, form_data={})
```

By default Flask routes only accept GET requests. The `methods=["GET", "POST"]` argument enables form submissions. A single route function handles both request types: a GET request renders the empty form, and a POST request processes the submitted data. `request.form` is a dictionary of all submitted form field values. `.strip()` removes leading and trailing whitespace from text input. The availability checkbox is handled with a conditional expression because HTML checkboxes only appear in the form data when checked. When unchecked, `request.form.get("available")` returns `None`, which the expression converts to `0`. When checked it returns `"on"`, which converts to `1`.

Before any database operation, validation is performed: the name field must not be empty, the category must be one of the four defined values, and the price must be convertible to a float and non-negative. If any validation fails, error messages are flashed and the form is re-rendered with `form_data=request.form` so the user's previous input is preserved. On success, the item is inserted and the user is redirected using `redirect(url_for("index"))`.

**The edit, delete, and toggle routes** follow the same structural patterns. The edit route uses a URL variable `<int:item_id>` which Flask extracts from the URL and passes to the function as an integer. It performs a `SELECT` to load the current item, then on POST submission runs an `UPDATE` SQL statement. The delete route only accepts POST requests and runs a `DELETE` statement. The toggle route reads the current `available` value and sets it to the opposite using `new_status = 0 if item["available"] else 1`.

**The report route** fetches all items and processes them in Python before rendering. It builds a dictionary keyed by category, with each entry holding the list of items in that category and running totals for count and availability. It also computes overall statistics including total item count, available count, average price, minimum price, and maximum price, all passed as named arguments to `render_template`.

**The entry point block:**

```python
if __name__ == "__main__":
    init_db()
    logger.info("Starting Restaurant Menu Manager...")
    app.run(debug=True)
```

This block executes only when `app.py` is run directly from the terminal. It does not execute when the file is imported by the test suite. `init_db()` is called here to ensure the database exists before the first request is handled. `debug=True` enables automatic server reloading on file save and detailed error pages during development.

---

### Step 6 — HTML Templates

Five HTML template files were created in the `templates` directory. All templates use Jinja2, the templating engine bundled with Flask. Jinja2 allows Python variables, loops, and conditional logic to be embedded directly in HTML using two syntactic forms: `{{ variable }}` to output a value and `{% statement %}` to execute logic such as loops and conditionals.

**base.html** serves as the shared layout inherited by all other templates. It defines the full HTML document structure including the `<head>` element, navigation bar, footer, and the flash message display block. Within it, `{% block content %}{% endblock %}` acts as a named insertion point. Any template that extends `base.html` can define its own `{% block content %}` section, and Jinja2 injects that content into the layout at that position. The navigation links use `url_for` to generate URLs from Python function names rather than hardcoded strings. The flash message section calls `get_flashed_messages(with_categories=true)`, retrieving any messages stored by `flash()` in the routes. Each message's category string — either `"success"` or `"danger"` — is embedded into the CSS class as `alert-{{ category }}`, producing green or red banners accordingly.

**index.html** extends `base.html` and fills the content block with the filter bar and item table. The filter bar renders one button per category by looping over the `categories` list. Each button links to `/?category={{ cat }}`. The `btn-active` class is conditionally applied using `{% if selected_category == cat %}` to highlight the currently active filter. The item table loops over the `items` list passed from the route. The price is formatted to two decimal places with `{{ "%.2f" | format(item.price) }}`. The category badge uses `{{ item.category | lower }}` to convert the category string to lowercase before embedding it in the CSS class name, producing `badge-appetizer`, `badge-main`, and so on, which match the corresponding CSS rules. The Edit button is a standard anchor tag. The Disable/Enable and Delete buttons are wrapped in `<form>` elements with `method="POST"` because browsers cannot send POST requests through anchor tags. The delete form includes an `onsubmit="return confirm(...)"` attribute that triggers a browser confirmation dialog before submission.

**add.html** extends `base.html` and renders the item creation form. Each input field's `value` attribute is populated using `{{ form_data.get('field_name', '') }}`. When the page is first visited, `form_data` is an empty dictionary and all fields render blank. When the form is submitted and validation fails, `form_data` contains the previously submitted values and the fields re-populate automatically, preserving the user's input. The category dropdown iterates over the `categories` list and adds `selected` to the option whose value matches the user's previous selection.

**edit.html** is structurally identical to `add.html` with one distinction: instead of reading from `form_data`, the input values are populated directly from the `item` object loaded from the database, for example `value="{{ item.name }}"`. The form action is set to `{{ url_for('edit_item', item_id=item.id) }}`, which generates the correct URL for the specific record being edited.

**report.html** extends `base.html` and renders the menu summary. The upper section displays six stat cards outputting the variables passed from the report route. The expression `{{ total_items - total_available }}` performs arithmetic directly in the template to derive the unavailable count without requiring a separate variable. The lower section loops over the `report_data` dictionary with `{% for category, data in report_data.items() %}`, rendering a separate table for each category. Unavailable items receive the CSS class `row-unavailable` through a conditional, which reduces their visual opacity to distinguish them from active items.

---

### Step 7 — Create the Stylesheet

A single CSS file in `static/css/style.css` handles all visual styling. It uses a system font stack for a native look on every platform, a composable button class system where a base `.btn` class shares structure and modifier classes like `.btn-primary` and `.btn-danger` define color, color-coded category badges that connect directly to the Jinja2 `| lower` filter in the templates, and a flexbox layout for the report summary stat cards.

---

### Step 8 — Write the Tests

A pytest test file in `tests/test_app.py` covers all thirteen test cases across every route. A fixture function creates a temporary file-based SQLite database before each test and deletes it after, ensuring tests are fully isolated from each other and from the real database. Tests verify page loads, category filtering, valid form submissions, input validation errors, item deletion, availability toggling, and report generation.

---

### Step 9 — Run the App

With the virtual environment active, running `python app.py` starts the Flask development server. The app is accessible at `http://127.0.0.1:5000` in any browser. The database is created and seeded automatically on first run.

---

### Step 10 — Run the Tests

Running `python -m pytest tests/ -v` executes all thirteen tests. The `-v` flag shows each test name and result individually. All thirteen pass.

---

### Step 11 — Create .gitignore

A `.gitignore` file tells Git to exclude the virtual environment folder, compiled Python files, the database file, and macOS system files. These are environment-specific and should never be committed to version control.

---

### Step 12 — Push to GitHub

Using Git and the GitHub CLI, a repository was initialized, all project files were staged and committed with a descriptive message, and everything was pushed to a new public repository named `d424 Cap task 3-4`.

---

## Result

The completed application demonstrates full CRUD functionality, input validation, error handling, structured logging, automated testing, and a report generation feature — all core requirements for the WGU D424 Software Engineering Capstone. The codebase is fully documented, tested, and version controlled on GitHub at:

**https://github.com/harrison-glitch/d424-Cap-task-3-4**
