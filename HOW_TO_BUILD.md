# How to Build the Restaurant Menu Manager — Complete Step-by-Step Guide

This guide walks you through building this entire project from scratch on macOS.
Every terminal command, every file, and every line of code is explained in plain English.

---

## What You Are Building

A web application that runs in your browser and lets you manage a restaurant menu.
You can view, add, edit, and delete menu items, toggle whether they are available,
and generate a summary report. It uses a real database to store everything.

---

## The Tools You Will Use

| Tool | What it is | Why |
|------|-----------|-----|
| Python 3 | Programming language | You already know it |
| Flask | Web framework | Turns Python into a web server |
| SQLite | Database | Built into Python, no setup needed |
| Jinja2 | HTML templating | Comes with Flask, lets HTML display Python data |
| pytest | Testing framework | Standard Python testing tool |
| Git | Version control | Tracks your changes |
| GitHub CLI (`gh`) | GitHub from the terminal | Creates and pushes repos without the browser |

---

## Before You Start — Check Your Setup

Open **Terminal** (press `Cmd + Space`, type `Terminal`, press Enter).

Run each of these to confirm they are installed:

```bash
python3 --version
```
You should see something like `Python 3.9.6` or newer. If you get `command not found`,
download Python from https://www.python.org/downloads/

```bash
git --version
```
You should see `git version 2.x.x`. Git comes with macOS developer tools. If missing,
run `xcode-select --install` and follow the prompts.

```bash
gh --version
```
You should see `gh version 2.x.x`. If missing, install it with:
```bash
brew install gh
```
If you don't have Homebrew either, install it first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## Step 1 — Create the Project Folder

In Terminal, run these commands one at a time. Press Enter after each one.

```bash
cd ~/Desktop
```
This moves you to your Desktop. You can use any folder you want — this is just easy to find.

```bash
mkdir restaurant-menu
```
`mkdir` means "make directory." This creates a new folder called `restaurant-menu`.

```bash
cd restaurant-menu
```
Moves you inside the folder you just created. All commands from here on run inside this folder.

```bash
mkdir templates
mkdir -p static/css
mkdir tests
```
- `mkdir templates` — Flask automatically looks in a folder called `templates` for your HTML files. The name must be exactly this.
- `mkdir -p static/css` — Flask looks in `static/` for CSS, images, and other files. The `-p` flag creates both `static/` and `css/` inside it at the same time.
- `mkdir tests` — Where your test files will live.

**Verify it worked:**
```bash
ls
```
`ls` lists the contents of the current folder. You should see:
```
static   templates   tests
```

Your folder structure now looks like this:
```
restaurant-menu/
├── templates/
├── static/
│   └── css/
└── tests/
```

---

## Step 2 — Set Up a Virtual Environment

A virtual environment is an isolated container for your Python packages. It keeps this
project's packages completely separate from every other Python project on your computer.
This prevents version conflicts and is standard practice for every Python project.

```bash
python3 -m venv venv
```
- `python3 -m venv` — runs Python's built-in virtual environment tool
- The last `venv` is the name of the folder it creates. Convention is to call it `venv`.

```bash
source venv/bin/activate
```
This activates the virtual environment. After running this, your terminal prompt will
change to show `(venv)` at the start, like this:
```
(venv) harrisonsmith@Harrisons-Mac restaurant-menu %
```
That `(venv)` prefix tells you the virtual environment is active. Any Python packages
you install now go into `venv/` and nowhere else.

**Important:** You need to run `source venv/bin/activate` every time you open a new
Terminal window to work on this project.

To deactivate it when you're done:
```bash
deactivate
```

---

## Step 3 — Create requirements.txt and Install Packages

Create the file:
```bash
touch requirements.txt
```
`touch` creates an empty file.

Now open it in a text editor. If you have VS Code:
```bash
code requirements.txt
```
Or open it with the built-in TextEdit:
```bash
open -e requirements.txt
```

Add these two lines exactly:
```
Flask==3.0.3
pytest==8.3.2
```

Save and close. Then install them:
```bash
pip install -r requirements.txt
```
- `pip` is Python's package installer
- `-r requirements.txt` means "install everything listed in this file"
- `==3.0.3` pins the exact version so anyone who clones your project gets the same version

You will see output like `Successfully installed Flask-3.0.3 ...`

**Verify it worked:**
```bash
pip list
```
You should see Flask and pytest in the list.


---

## Step 4 — Create database.py

This file handles everything related to the database: connecting to it and building it.

In Terminal:
```bash
touch database.py
code database.py
```

Type or paste the full file contents:

```python
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
```

Save the file.

### What every part does

**The imports at the top:**
```python
import sqlite3
import os
```
- `sqlite3` — Python's built-in library for working with SQLite databases. No install needed.
- `os` — Python's built-in library for working with files and folder paths.

---

**The database path:**
```python
DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")
```
This builds the full file path to where the database file will be saved.

Breaking it down piece by piece:
- `__file__` — a Python built-in that holds the path of the current file, e.g. `/Users/harrisonsmith/Desktop/restaurant-menu/database.py`
- `os.path.dirname(__file__)` — strips the filename off the end, leaving just the folder: `/Users/harrisonsmith/Desktop/restaurant-menu/`
- `os.path.join(..., "menu.db")` — joins the folder path with `menu.db` to get the full path: `/Users/harrisonsmith/Desktop/restaurant-menu/menu.db`

Why not just write `"menu.db"` directly? Because depending on which folder Terminal is in
when you run the app, a plain filename might resolve to the wrong location. Using the
absolute path based on `__file__` always works correctly no matter where you run from.

---

**get_connection():**
```python
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```
This function opens a connection to the database and returns it.

- `sqlite3.connect(DB_PATH)` — opens the `.db` file. If the file doesn't exist yet, SQLite creates it automatically.
- `conn.row_factory = sqlite3.Row` — this is important. Without it, when you fetch rows from the database they come back as plain tuples. You'd have to access data by index: `row[0]`, `row[1]`, etc. With `sqlite3.Row`, you can access data by column name: `row["name"]`, `row["price"]`. Much more readable.

Every route in `app.py` calls `get_connection()` when it needs to talk to the database.

---

**init_db():**
```python
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
```
Opens a connection and creates a cursor. A cursor is the object you use to actually
run SQL commands.

```python
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
This creates the database table. `CREATE TABLE IF NOT EXISTS` means it only creates the
table if it doesn't already exist — so you can safely run this every time the app starts
without wiping out your data.

The columns explained:
- `id INTEGER PRIMARY KEY AUTOINCREMENT` — a unique number that automatically counts up for each new row. You never set this yourself.
- `name TEXT NOT NULL` — the item name. `NOT NULL` means this field is required — SQLite will reject the row if it's missing.
- `category TEXT NOT NULL` — Appetizer, Main, Dessert, or Drink. Also required.
- `description TEXT` — no `NOT NULL`, so this is optional.
- `price REAL NOT NULL` — `REAL` is SQLite's type for decimal numbers (like 9.99).
- `available INTEGER NOT NULL DEFAULT 1` — SQLite has no true boolean type, so we use integers: `1` = available, `0` = unavailable. `DEFAULT 1` means new items are available unless you say otherwise.

```python
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO menu_items (...) VALUES (?, ?, ?, ?, ?)",
            sample_items
        )
```
After creating the table, this checks if it's empty. If it is, it inserts the sample
data so the app has something to show on first run.

The `?` placeholders are called a parameterized query. This is a security requirement —
never put variables directly into an SQL string using string formatting like `f"INSERT INTO ... VALUES ({name})"`.
That opens your app to SQL injection attacks where someone types SQL code into a form field
and damages or reads your database. The `?` approach passes values separately so the database
treats them as data only, never as SQL commands.

```python
    conn.commit()
    conn.close()
```
- `conn.commit()` — saves all the changes. Without this, the inserts are not actually written to disk.
- `conn.close()` — closes the connection and frees up the resource.

---

**Test it works:**
```bash
python database.py
```
You should see: `Database initialized successfully.`

Then check the file was created:
```bash
ls
```
You should now see `menu.db` in the folder.


---

## Step 5 — Create app.py

This is the main file. It creates the web server and defines every URL the app responds to.

```bash
touch app.py
code app.py
```

### 5a — Imports and App Setup

At the very top of `app.py`:

```python
"""
app.py - Main Flask application for Restaurant Menu Manager.
"""

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

**Line by line:**

`import logging` — Python's built-in logging library. Better than print statements
because log lines include a timestamp and severity level.

`from flask import Flask, render_template, request, redirect, url_for, flash` — imports
the specific Flask tools we need:
- `Flask` — the class that creates the app
- `render_template` — loads an HTML file and fills in variables
- `request` — lets you read incoming data (form inputs, URL parameters)
- `redirect` — sends the user to a different URL
- `url_for` — generates a URL from a function name
- `flash` — stores a one-time message (like "Item saved!") to show on the next page

`from database import get_connection, init_db` — pulls in the two functions from the
`database.py` file you just created.

`app = Flask(__name__)` — creates the Flask application object. `__name__` is a Python
built-in that equals the current module's name. Flask uses it to figure out where to
look for your `templates/` and `static/` folders — they need to be in the same directory
as the file where `Flask(__name__)` is called.

`app.secret_key = "restaurant-menu-secret-key"` — Flask needs a secret key to sign
the session cookie that stores flash messages. This can be any string. In a real
production app you would load this from an environment variable, not hardcode it.

`logging.basicConfig(...)` — configures the logger so every log line looks like:
`2026-08-17 11:00:00,000 [INFO] Loaded 10 menu items`

`logger = logging.getLogger(__name__)` — creates a logger named after this file.
You use it throughout the file with `logger.info(...)` and `logger.error(...)`.

`CATEGORIES = ["Appetizer", "Main", "Dessert", "Drink"]` — defined once at the top
so you never type this list more than once. Every route and template that needs it
references this one variable. If you add a category later, you change it in one place.

---

### 5b — The Index Route (View All Items)

```python
@app.route("/")
def index():
    """Display all menu items, optionally filtered by category."""
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

    return render_template(
        "index.html",
        items=items,
        categories=CATEGORIES,
        selected_category=category_filter
    )
```

**`@app.route("/")`** — This is a decorator. It tells Flask: "when someone visits the
URL `/`, run the function directly below this line." The `/` is the homepage.

**`def index():`** — the function that runs when the homepage is visited.

**`request.args.get("category", "")`** — `request.args` is a dictionary of URL query
parameters. If the browser visits `/?category=Main`, then `request.args.get("category")`
returns `"Main"`. The `""` is the default if no `category` parameter is in the URL.
This is how the filter buttons at the top of the page work — clicking "Main" navigates
to `/?category=Main`, and this line reads that value.

**`try: ... except Exception as e:`** — Every database call is wrapped in try/except.
If something goes wrong (database file corrupted, disk full, etc.), the error is caught,
logged, and a friendly message is shown to the user instead of a crash. `items = []` in
the except block means the page still renders — just empty — instead of showing a
Python error page.

**`conn.execute(...).fetchall()`** — runs the SQL query and returns all matching rows
as a list. `fetchall()` returns every row. If you only wanted one row you would use
`fetchone()`.

**`"SELECT * FROM menu_items WHERE category = ? ORDER BY category, name"`** — this SQL
reads as: "get all columns from the menu_items table, but only rows where the category
column matches the value I'm about to provide, and sort the results by category then
by name alphabetically." The `?` is filled in by the `(category_filter,)` tuple that
follows. Note the trailing comma — `(category_filter,)` is a tuple with one item.
Without the comma, Python would treat it as just parentheses around a string, not a tuple,
and SQLite would reject it.

**`render_template("index.html", items=items, categories=CATEGORIES, selected_category=category_filter)`**
— loads `templates/index.html` and makes these Python variables available inside the
HTML file:
- `items` — the list of database rows
- `categories` — the list of category names for the filter buttons
- `selected_category` — which category is currently filtered (so the active button can be highlighted)

---

### 5c — The Add Route

```python
@app.route("/add", methods=["GET", "POST"])
def add_item():
    """Add a new menu item."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()
        available = 1 if request.form.get("available") else 0

        errors = []
        if not name:
            errors.append("Name is required.")
        if category not in CATEGORIES:
            errors.append("Invalid category.")
        try:
            price = float(price_raw)
            if price < 0:
                errors.append("Price must be a positive number.")
        except ValueError:
            errors.append("Price must be a valid number.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("add.html", categories=CATEGORIES, form_data=request.form)

        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO menu_items (name, category, description, price, available) VALUES (?, ?, ?, ?, ?)",
                (name, category, description, price, available)
            )
            conn.commit()
            conn.close()
            logger.info("Added menu item: %s (%s) $%.2f", name, category, price)
            flash(f"'{name}' added successfully!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            logger.error("Failed to add item: %s", e)
            flash("Error adding item. Please try again.", "danger")

    return render_template("add.html", categories=CATEGORIES, form_data={})
```

**`methods=["GET", "POST"]`** — by default, Flask routes only accept GET requests (when
a browser visits a URL normally). You have to explicitly list POST to allow form submissions.
This one route handles two situations using the same URL `/add`.

**`if request.method == "POST":`** — when the user submits the form, the browser sends
a POST request. When the user first visits the page, it's a GET request. This `if` block
only runs on form submission.

**`request.form.get("name", "").strip()`** — `request.form` is a dictionary of the form
fields the user submitted. `.strip()` removes any accidental spaces the user may have
typed at the start or end.

**`available = 1 if request.form.get("available") else 0`** — HTML checkboxes work
differently from text inputs. If a checkbox is checked, the browser includes it in the
form data with the value `"on"`. If it is unchecked, the browser sends nothing at all
for that field. So `request.form.get("available")` returns `"on"` (truthy) when checked
and `None` (falsy) when unchecked. This one-liner converts that to `1` or `0` for the
database.

**The validation block** — before touching the database, we verify the data makes sense:
- name can't be empty
- category must be one of our four valid options (not just anything the user types)
- price must be a number and must not be negative

If any check fails, `flash()` stores an error message and we re-render the form. Passing
`form_data=request.form` back to the template lets the form re-fill itself with what the
user already typed — so they don't have to retype everything just because the price was wrong.

**`redirect(url_for("index"))`** — after a successful save, send the user back to the
homepage. `url_for("index")` generates the URL `"/"` by looking up the function named
`index`. Using `url_for` instead of hardcoding `"/"` means if you ever change the route,
the redirect updates automatically.

**The last line runs on GET requests** — when the user first visits `/add`, `request.method`
is `"GET"` so the `if` block is skipped entirely, and we just render the empty form.
`form_data={}` provides an empty dict so the template doesn't crash trying to look up
previous values.

---

### 5d — The Edit Route

```python
@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    """Edit an existing menu item."""
    try:
        conn = get_connection()
        item = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
        conn.close()
    except Exception as e:
        logger.error("Failed to load item %d: %s", item_id, e)
        flash("Error loading item.", "danger")
        return redirect(url_for("index"))

    if item is None:
        flash("Item not found.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        # ... same validation as add_item ...
        conn.execute(
            "UPDATE menu_items SET name=?, category=?, description=?, price=?, available=? WHERE id=?",
            (name, category, description, price, available, item_id)
        )
        conn.commit()
        conn.close()
        flash(f"'{name}' updated successfully!", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", item=item, categories=CATEGORIES)
```

**`/edit/<int:item_id>`** — the `<int:item_id>` part is a URL variable. When someone
visits `/edit/3`, Flask automatically extracts the `3`, converts it to an integer, and
passes it into the function as `item_id`. The `int:` prefix tells Flask to only match
URLs where that segment is an integer — so `/edit/abc` would return a 404 error.

**`fetchone()`** — returns a single row instead of a list. If no row matches the id,
it returns `None`. The `if item is None:` check handles that case gracefully.

The rest follows the same GET/POST pattern as the add route, except the SQL command
is `UPDATE` instead of `INSERT`.

---

### 5e — The Delete Route

```python
@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    """Delete a menu item by ID."""
    try:
        conn = get_connection()
        item = conn.execute("SELECT name FROM menu_items WHERE id = ?", (item_id,)).fetchone()
        if item:
            conn.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
            conn.commit()
            flash(f"'{item['name']}' deleted.", "success")
        else:
            flash("Item not found.", "danger")
        conn.close()
    except Exception as e:
        logger.error("Failed to delete item %d: %s", item_id, e)
        flash("Error deleting item.", "danger")

    return redirect(url_for("index"))
```

**`methods=["POST"]` only** — this route only accepts POST requests, never GET.
This is intentional. If it accepted GET, someone could delete items just by visiting
a URL — or a browser could accidentally delete items when pre-fetching links. Delete
actions must be triggered by a form submission.

We look up the item first to get its name for the confirmation message. Then we run
`DELETE FROM menu_items WHERE id = ?`. After deleting, we always redirect back to the
homepage.

---

### 5f — The Toggle Route

```python
@app.route("/toggle/<int:item_id>", methods=["POST"])
def toggle_availability(item_id):
    """Toggle a menu item's availability between available and unavailable."""
    try:
        conn = get_connection()
        item = conn.execute("SELECT name, available FROM menu_items WHERE id = ?", (item_id,)).fetchone()
        if item:
            new_status = 0 if item["available"] else 1
            conn.execute("UPDATE menu_items SET available = ? WHERE id = ?", (new_status, item_id))
            conn.commit()
            status_label = "available" if new_status else "unavailable"
            flash(f"'{item['name']}' marked as {status_label}.", "success")
        else:
            flash("Item not found.", "danger")
        conn.close()
    except Exception as e:
        logger.error("Failed to toggle item %d: %s", item_id, e)
        flash("Error updating availability.", "danger")

    return redirect(url_for("index"))
```

**`new_status = 0 if item["available"] else 1`** — reads the current value and flips it.
If it's currently `1` (available), `new_status` becomes `0`. If it's `0`, `new_status`
becomes `1`. This is the toggle logic in one line.

---

### 5g — The Report Route

```python
@app.route("/report")
def report():
    """Generate a summary report of the menu."""
    try:
        conn = get_connection()
        all_items = conn.execute("SELECT * FROM menu_items ORDER BY category, name").fetchall()

        report_data = {}
        for item in all_items:
            cat = item["category"]
            if cat not in report_data:
                report_data[cat] = {"menu_items": [], "total": 0, "available": 0}
            report_data[cat]["menu_items"].append(item)
            report_data[cat]["total"] += 1
            if item["available"]:
                report_data[cat]["available"] += 1

        total_items = len(all_items)
        total_available = sum(1 for i in all_items if i["available"])
        prices = [i["price"] for i in all_items]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        conn.close()
    except Exception as e:
        logger.error("Failed to generate report: %s", e)
        flash("Error generating report.", "danger")
        return redirect(url_for("index"))

    return render_template("report.html", report_data=report_data,
                           total_items=total_items, total_available=total_available,
                           avg_price=avg_price, min_price=min_price, max_price=max_price)
```

This route does the number-crunching in Python before passing the results to the template.

**Building `report_data`:** the loop groups every item by category into a dictionary.
After the loop, `report_data` looks like:
```python
{
    "Appetizer": {"menu_items": [...], "total": 2, "available": 2},
    "Main":      {"menu_items": [...], "total": 5, "available": 4},
    ...
}
```
The template then loops over this structure to display a table per category.

**`sum(1 for i in all_items if i["available"])`** — this is a generator expression. It
is the same as writing:
```python
count = 0
for i in all_items:
    if i["available"]:
        count += 1
```
Just written in one line. It counts how many items have `available == 1`.

**`avg_price = sum(prices) / len(prices) if prices else 0`** — the `if prices else 0`
part prevents a division-by-zero error if the menu is completely empty.

---

### 5h — The Entry Point

At the very bottom of `app.py`:

```python
if __name__ == "__main__":
    init_db()
    logger.info("Starting Restaurant Menu Manager...")
    app.run(debug=True)
```

**`if __name__ == "__main__":`** — this block only runs when you execute `python app.py`
directly in the terminal. When pytest imports `app.py` to run tests, `__name__` is not
`"__main__"`, so this block is skipped. This is standard Python practice for separating
"run this file directly" from "import this file."

**`init_db()`** — creates the database and seeds sample data on first run.

**`app.run(debug=True)`** — starts the Flask development server.
`debug=True` enables two things:
1. The server automatically restarts when you save a file — no need to stop and restart manually.
2. If there's an error, Flask shows you a detailed error page in the browser instead of a plain 500 page.

Never deploy with `debug=True`. It exposes your code and allows remote code execution.


---

## Step 6 — Create the HTML Templates

Flask uses a templating engine called **Jinja2** to combine HTML with Python data.
All template files go in the `templates/` folder.

### How Jinja2 syntax works

Before looking at the files, here are the three Jinja2 patterns used throughout:

**Output a variable:**
```html
{{ item.name }}
```
Double curly braces print a variable's value into the HTML.

**Run logic (if/for):**
```html
{% if item.available %}
    <span>Available</span>
{% else %}
    <span>Unavailable</span>
{% endif %}

{% for item in items %}
    <tr><td>{{ item.name }}</td></tr>
{% endfor %}
```
Curly brace + percent sign runs Python-style logic. Every `{% if %}` needs `{% endif %}`,
every `{% for %}` needs `{% endfor %}`.

**Template inheritance:**
```html
{% extends "base.html" %}
{% block content %}
    ... page content here ...
{% endblock %}
```
Child templates "extend" a parent template and fill in named blocks. This is how every
page shares the same nav bar and footer without repeating that HTML in every file.

---

### 6a — base.html (The Shared Layout)

```bash
touch templates/base.html
code templates/base.html
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Restaurant Menu Manager{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav>
        <div class="nav-brand">🍽️ Menu Manager</div>
        <div class="nav-links">
            <a href="{{ url_for('index') }}">Menu</a>
            <a href="{{ url_for('add_item') }}">+ Add Item</a>
            <a href="{{ url_for('report') }}">Report</a>
        </div>
    </nav>

    <main>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>Restaurant Menu Manager &mdash; WGU Software Engineering Capstone</p>
    </footer>
</body>
</html>
```

**`{% block title %}...{% endblock %}`** — defines a replaceable block. The default
value is "Restaurant Menu Manager". Child templates override this to set a custom
page title like "Add Item - Restaurant Menu Manager".

**`{{ url_for('static', filename='css/style.css') }}`** — generates the correct URL
to your CSS file. Flask's `url_for('static', ...)` always produces the right path
regardless of where your app is deployed. Never hardcode paths like `/static/css/style.css`.

**`{{ url_for('index') }}`** — generates the URL `"/"` by looking up the function
named `index` in `app.py`. Same for `url_for('add_item')` → `"/add"`,
`url_for('report')` → `"/report"`. If you change a route URL in `app.py`, every
`url_for` using that function name updates automatically.

**The flash message block:**
```html
{% with messages = get_flashed_messages(with_categories=true) %}
```
`get_flashed_messages` is a Jinja2 global function Flask provides. It retrieves any
messages stored by `flash()` in your routes. `with_categories=true` means each message
comes back as a `(category, message)` tuple, like `("success", "Item saved!")` or
`("danger", "Name is required.")`. The category is used as a CSS class:
`alert-success` → green, `alert-danger` → red.

**`{% block content %}{% endblock %}`** — this empty block is the slot where each
child template's content gets inserted.

---

### 6b — index.html (The Menu List Page)

```bash
touch templates/index.html
code templates/index.html
```

```html
{% extends "base.html" %}
{% block title %}Menu - Restaurant Menu Manager{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Menu Items</h1>
    <a href="{{ url_for('add_item') }}" class="btn btn-primary">+ Add Item</a>
</div>

<div class="filter-bar">
    <span>Filter by category:</span>
    <a href="{{ url_for('index') }}" class="btn btn-sm {% if not selected_category %}btn-active{% endif %}">All</a>
    {% for cat in categories %}
        <a href="{{ url_for('index', category=cat) }}"
           class="btn btn-sm {% if selected_category == cat %}btn-active{% endif %}">
            {{ cat }}
        </a>
    {% endfor %}
</div>

{% if items %}
<table>
    <thead>
        <tr>
            <th>Name</th><th>Category</th><th>Description</th>
            <th>Price</th><th>Status</th><th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for item in items %}
        <tr class="{% if not item.available %}row-unavailable{% endif %}">
            <td><strong>{{ item.name }}</strong></td>
            <td><span class="badge badge-{{ item.category | lower }}">{{ item.category }}</span></td>
            <td>{{ item.description or "—" }}</td>
            <td>${{ "%.2f" | format(item.price) }}</td>
            <td>
                {% if item.available %}
                    <span class="status-available">Available</span>
                {% else %}
                    <span class="status-unavailable">Unavailable</span>
                {% endif %}
            </td>
            <td class="actions">
                <a href="{{ url_for('edit_item', item_id=item.id) }}" class="btn btn-sm btn-secondary">Edit</a>

                <form action="{{ url_for('toggle_availability', item_id=item.id) }}" method="POST" style="display:inline;">
                    <button type="submit" class="btn btn-sm btn-toggle">
                        {% if item.available %}Disable{% else %}Enable{% endif %}
                    </button>
                </form>

                <form action="{{ url_for('delete_item', item_id=item.id) }}" method="POST" style="display:inline;"
                      onsubmit="return confirm('Delete {{ item.name }}? This cannot be undone.');">
                    <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<div class="empty-state">
    <p>No menu items found. <a href="{{ url_for('add_item') }}">Add the first one!</a></p>
</div>
{% endif %}
{% endblock %}
```

**`url_for('index', category=cat)`** — passing extra keyword arguments to `url_for`
adds them as query parameters. So `url_for('index', category='Main')` generates
`/?category=Main`. That's how the filter buttons work.

**`{% if not selected_category %}btn-active{% endif %}`** — conditionally adds the
`btn-active` CSS class to highlight which filter button is currently selected.

**`{{ item.category | lower }}`** — the `|` is a Jinja2 filter. `lower` converts the
string to lowercase. So `"Appetizer"` becomes `"appetizer"`, making the CSS class
`badge-appetizer` which matches the CSS rule `.badge-appetizer { background: purple; }`.

**`{{ "%.2f" | format(item.price) }}`** — formats the price as a decimal with exactly
two places. `9.9` becomes `"9.90"`.

**`{{ item.description or "—" }}`** — if `description` is empty or `None`, shows a
dash instead of a blank cell.

**Why delete uses a `<form>` not an `<a>` tag:** Browsers only send POST requests via
forms. Using `<a href="/delete/1">` would be a GET request, which is wrong for a
destructive action. The `onsubmit="return confirm(...)"` shows a browser confirmation
dialog before the form actually submits.

---

### 6c — add.html (The Add Form)

```bash
touch templates/add.html
code templates/add.html
```

```html
{% extends "base.html" %}
{% block title %}Add Item - Restaurant Menu Manager{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Add Menu Item</h1>
    <a href="{{ url_for('index') }}" class="btn btn-secondary">← Back to Menu</a>
</div>

<div class="form-container">
    <form method="POST" action="{{ url_for('add_item') }}">

        <div class="form-group">
            <label for="name">Item Name *</label>
            <input type="text" id="name" name="name"
                   value="{{ form_data.get('name', '') }}"
                   placeholder="e.g. Cheeseburger" required>
        </div>

        <div class="form-group">
            <label for="category">Category *</label>
            <select id="category" name="category" required>
                <option value="">-- Select Category --</option>
                {% for cat in categories %}
                    <option value="{{ cat }}"
                        {% if form_data.get('category') == cat %}selected{% endif %}>
                        {{ cat }}
                    </option>
                {% endfor %}
            </select>
        </div>

        <div class="form-group">
            <label for="description">Description</label>
            <textarea id="description" name="description"
                      placeholder="Brief description of the item...">{{ form_data.get('description', '') }}</textarea>
        </div>

        <div class="form-group">
            <label for="price">Price ($) *</label>
            <input type="number" id="price" name="price"
                   value="{{ form_data.get('price', '') }}"
                   step="0.01" min="0" placeholder="0.00" required>
        </div>

        <div class="form-group form-check">
            <input type="checkbox" id="available" name="available"
                   {% if form_data.get('available', True) %}checked{% endif %}>
            <label for="available">Available on menu</label>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Add Item</button>
            <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancel</a>
        </div>

    </form>
</div>
{% endblock %}
```

**`value="{{ form_data.get('name', '') }}"`** — if validation failed and the form was
re-rendered, `form_data` contains what the user previously typed. This re-fills the
input so they don't have to type it all again. On the first visit, `form_data` is `{}`
(empty dict), so `.get('name', '')` returns an empty string.

**`{% if form_data.get('category') == cat %}selected{% endif %}`** — re-selects the
dropdown option the user had chosen before the validation error.

**`step="0.01" min="0"`** — HTML attributes on the price input. `step="0.01"` allows
decimal values. `min="0"` prevents negative numbers at the browser level (your Python
validation is the real enforcement, but this gives immediate feedback).

---

### 6d — edit.html (The Edit Form)

```bash
touch templates/edit.html
code templates/edit.html
```

This is almost identical to `add.html`, but instead of reading from `form_data`,
it reads directly from the `item` object loaded from the database:

```html
<input type="text" id="name" name="name" value="{{ item.name }}" required>
```

And the form submits to the edit route with the item's id:
```html
<form method="POST" action="{{ url_for('edit_item', item_id=item.id) }}">
```

---

### 6e — report.html (The Report Page)

```bash
touch templates/report.html
code templates/report.html
```

```html
{% extends "base.html" %}
{% block title %}Menu Report - Restaurant Menu Manager{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Menu Report</h1>
    <a href="{{ url_for('index') }}" class="btn btn-secondary">← Back to Menu</a>
</div>

<div class="report-summary">
    <div class="stat-card">
        <div class="stat-number">{{ total_items }}</div>
        <div class="stat-label">Total Items</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ total_available }}</div>
        <div class="stat-label">Available</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">{{ total_items - total_available }}</div>
        <div class="stat-label">Unavailable</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">${{ "%.2f" | format(avg_price) }}</div>
        <div class="stat-label">Avg Price</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">${{ "%.2f" | format(min_price) }}</div>
        <div class="stat-label">Lowest Price</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">${{ "%.2f" | format(max_price) }}</div>
        <div class="stat-label">Highest Price</div>
    </div>
</div>

{% for category, data in report_data.items() %}
<div class="report-section">
    <h2>{{ category }}
        <span class="category-count">({{ data.total }} items, {{ data.available }} available)</span>
    </h2>
    <table>
        <thead>
            <tr><th>Name</th><th>Description</th><th>Price</th><th>Status</th></tr>
        </thead>
        <tbody>
            {% for item in data.menu_items %}
            <tr class="{% if not item.available %}row-unavailable{% endif %}">
                <td><strong>{{ item.name }}</strong></td>
                <td>{{ item.description or "—" }}</td>
                <td>${{ "%.2f" | format(item.price) }}</td>
                <td>
                    {% if item.available %}
                        <span class="status-available">Available</span>
                    {% else %}
                        <span class="status-unavailable">Unavailable</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endfor %}
{% endblock %}
```

**`{% for category, data in report_data.items() %}`** — `.items()` on a Python dict
returns key-value pairs. Here `category` gets the string like `"Main"` and `data` gets
the dictionary of items/totals for that category.

**`{{ total_items - total_available }}`** — you can do math directly inside `{{ }}`.


---

## Step 7 — Create the Stylesheet

```bash
touch static/css/style.css
code static/css/style.css
```

The CSS controls every visual aspect of the app. Key sections explained:

**Reset and base:**
```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f5f5;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}
```
`box-sizing: border-box` makes sizing predictable — padding and borders are included
in element dimensions instead of added on top of them.

The font stack `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` uses
the operating system's default font on every platform: San Francisco on Mac/iOS,
Segoe UI on Windows, Roboto on Android. No font file download needed.

`display: flex; flex-direction: column` on the body lets the footer stick to the bottom
of the page even when there isn't much content.

**Buttons — base class plus modifiers:**
```css
.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    font-size: 0.9rem;
    text-decoration: none;
    transition: opacity 0.2s;
}
.btn:hover { opacity: 0.85; }
.btn-primary   { background: #3498db; color: white; }
.btn-secondary { background: #95a5a6; color: white; }
.btn-danger    { background: #e74c3c; color: white; }
.btn-toggle    { background: #f39c12; color: white; }
.btn-sm        { padding: 0.3rem 0.7rem; font-size: 0.82rem; }
```
`.btn` defines the shared styles. `.btn-primary`, `.btn-danger`, etc. only define the
color. In HTML you stack them: `class="btn btn-primary"` or `class="btn btn-sm btn-danger"`.
This pattern means you never write the same border-radius or padding more than once.

**Category badges:**
```css
.badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px;
         font-size: 0.78rem; font-weight: 600; color: white; }
.badge-appetizer { background: #9b59b6; }
.badge-main      { background: #e67e22; }
.badge-dessert   { background: #e91e8c; }
.badge-drink     { background: #1abc9c; }
```
In `index.html`, the template outputs `badge-{{ item.category | lower }}`. The `| lower`
Jinja2 filter converts "Appetizer" → "appetizer", so the class becomes `badge-appetizer`
which matches this CSS rule. This is how the colored category pills are generated
dynamically without any JavaScript.

**Alert colors:**
```css
.alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.alert-danger  { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
```
These match the category strings passed to `flash()` in `app.py`. `flash("...", "success")`
produces `<div class="alert alert-success">` in the template, which triggers the green styling.

**Report stat cards:**
```css
.report-summary { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem; }
.stat-card {
    background: white;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    min-width: 120px;
    flex: 1;
}
.stat-number { font-size: 1.8rem; font-weight: 700; color: #2c3e50; }
.stat-label  { font-size: 0.8rem; color: #888; margin-top: 0.3rem; text-transform: uppercase; }
```
`display: flex` on `.report-summary` puts the cards side by side. `flex: 1` on each
card makes them share space equally. `flex-wrap: wrap` lets them wrap to the next line
on small screens.

Copy the full CSS from `static/css/style.css` in the project.

---

## Step 8 — Create the Tests

```bash
touch tests/test_app.py
code tests/test_app.py
```

Also create an empty `__init__.py` so Python treats `tests/` as a package:
```bash
touch tests/__init__.py
```

Full test file:

```python
"""
tests/test_app.py - Unit and integration tests for Restaurant Menu Manager.
"""

import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import database


@pytest.fixture
def client():
    """Set up a test Flask client with a temporary file-based database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    original_path = database.DB_PATH
    database.DB_PATH = db_path

    from app import app as flask_app
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"

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

    database.DB_PATH = original_path
    os.unlink(db_path)


def test_index_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Test Burger" in response.data

def test_index_category_filter(client):
    response = client.get("/?category=Main")
    assert response.status_code == 200
    assert b"Test Burger" in response.data
    assert b"Test Salad" not in response.data

def test_add_item_get(client):
    response = client.get("/add")
    assert response.status_code == 200
    assert b"Add Menu Item" in response.data

def test_add_item_post_valid(client):
    response = client.post("/add", data={
        "name": "New Pizza", "category": "Main",
        "description": "Cheese pizza", "price": "11.99", "available": "on"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"New Pizza" in response.data

def test_add_item_post_missing_name(client):
    response = client.post("/add", data={
        "name": "", "category": "Main", "price": "9.99"
    }, follow_redirects=True)
    assert b"Name is required" in response.data

def test_add_item_post_invalid_price(client):
    response = client.post("/add", data={
        "name": "Bad Item", "category": "Main", "price": "not-a-price"
    }, follow_redirects=True)
    assert b"valid number" in response.data

def test_edit_item_get(client):
    response = client.get("/edit/1")
    assert response.status_code == 200
    assert b"Test Burger" in response.data

def test_edit_item_post_valid(client):
    response = client.post("/edit/1", data={
        "name": "Updated Burger", "category": "Main",
        "description": "Updated", "price": "12.99", "available": "on"
    }, follow_redirects=True)
    assert b"Updated Burger" in response.data

def test_edit_item_not_found(client):
    response = client.get("/edit/9999", follow_redirects=True)
    assert b"not found" in response.data

def test_delete_item(client):
    response = client.post("/delete/1", follow_redirects=True)
    assert b"deleted" in response.data
    assert b"A test burger" not in response.data

def test_delete_nonexistent_item(client):
    response = client.post("/delete/9999", follow_redirects=True)
    assert b"not found" in response.data

def test_toggle_availability(client):
    response = client.post("/toggle/1", follow_redirects=True)
    assert b"unavailable" in response.data

def test_report_loads(client):
    response = client.get("/report")
    assert response.status_code == 200
    assert b"Menu Report" in response.data
    assert b"Total Items" in response.data
```

### What every part of the test file does

**`sys.path.insert(0, ...)`** — adds the project root to Python's module search path
so the test file can `import database` and `from app import app` even though the test
file lives in a subdirectory.

**The `@pytest.fixture` decorator:**
A fixture is a function that sets up state before tests and tears it down after.
Any test function that lists `client` as a parameter automatically gets the test
client created by this fixture. pytest handles the setup and teardown automatically.

**Why a temp file instead of `:memory:`:**
SQLite's in-memory database (`:memory:`) only exists inside the connection that created it.
When your Flask app opens a new connection to handle a request, it would get a completely
fresh, empty database — not the one the fixture set up. By using a temp file
(`tempfile.mkstemp()`), all connections within the test share the same database file.

`tempfile.mkstemp()` returns two things: a file descriptor (`db_fd`) and the file path
(`db_path`). We immediately close the file descriptor with `os.close(db_fd)` because
SQLite will manage the file itself.

**`database.DB_PATH = db_path`** — redirects the database module to use the temp file
instead of the real `menu.db`. We save the original path first and restore it after
the test so other tests aren't affected.

**`yield test_client`** — the `yield` is the handoff to the test. Everything before
`yield` is setup. The test runs. Everything after `yield` is teardown — we restore the
original DB path and delete the temp file with `os.unlink(db_path)`.

**`follow_redirects=True`** — after a successful add/edit/delete, the app redirects
to the homepage. This option tells the test client to follow that redirect automatically
so the final response is the homepage, not a 302 redirect response.

**`response.data`** — the raw HTML bytes of the response. Note the `b""` prefix on
strings in assertions — `b"Test Burger"` is a bytes literal, because `response.data`
is bytes, not a regular string.

---

## Step 9 — Run the App

Make sure your virtual environment is active (you should see `(venv)` in the prompt):
```bash
source venv/bin/activate
```

Start the app:
```bash
python app.py
```

You will see output like:
```
2026-08-17 11:00:00 [INFO] Starting Restaurant Menu Manager...
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Open your browser and go to: **http://127.0.0.1:5000**

You should see the menu with the 10 sample items.

To stop the server: press `Control + C` in Terminal.

---

## Step 10 — Run the Tests

With the virtual environment active:
```bash
python -m pytest tests/ -v
```

- `-v` means "verbose" — shows each test name and its result
- You should see `13 passed`

If any test fails, pytest shows exactly which assertion failed and what the actual
value was. Read the error message carefully — it usually tells you exactly what is wrong.

To run a single test:
```bash
python -m pytest tests/test_app.py::test_index_loads -v
```

---

## Step 11 — Create .gitignore

Before pushing to GitHub, tell git to ignore files that shouldn't be committed:

```bash
touch .gitignore
code .gitignore
```

Add these lines:
```
venv/
__pycache__/
*.pyc
*.db
.env
.DS_Store
```

- `venv/` — thousands of package files, should never be in version control
- `__pycache__/` — Python's compiled bytecode cache, auto-generated
- `*.pyc` — compiled Python files
- `*.db` — the SQLite database file. Each environment has its own database.
- `.env` — environment variables file (secrets, API keys — never commit these)
- `.DS_Store` — macOS folder metadata files, irrelevant to the project

---

## Step 12 — Push to GitHub

First, authenticate the GitHub CLI if you haven't:
```bash
gh auth login
```
Follow the prompts — choose GitHub.com, HTTPS, and log in with your browser.

Then initialize git, commit, and create the repo:
```bash
git init
```
Initializes a git repository in the current folder. Creates a hidden `.git/` folder.

```bash
git add .
```
Stages all files for commit. The `.` means "everything in this folder" (respecting
`.gitignore`, so `venv/` and `*.db` are excluded).

```bash
git status
```
Shows what is staged. Run this before committing to confirm only the right files are included.

```bash
git commit -m "feat: initial Restaurant Menu Manager app"
```
Creates the first commit. The `-m` flag sets the commit message. Use a clear, descriptive
message. The `feat:` prefix follows conventional commits format — common in professional
development.

```bash
gh repo create "your-repo-name" --public --description "Your description here" --source . --push
```
- Creates the GitHub repository
- `--public` makes it visible on your profile
- `--source .` uses the current folder
- `--push` pushes your commit to GitHub immediately

After it runs, it prints the repository URL. Open it in your browser to confirm everything
is there.

For future changes, the workflow is:
```bash
git add .
git commit -m "description of what you changed"
git push
```

---

## Complete File Structure

After all steps, your project looks like this:

```
restaurant-menu/
├── .gitignore
├── README.md
├── HOW_TO_BUILD.md
├── app.py
├── database.py
├── requirements.txt
├── menu.db              ← created automatically on first run (not in git)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add.html
│   ├── edit.html
│   └── report.html
├── static/
│   └── css/
│       └── style.css
├── tests/
│   ├── __init__.py
│   └── test_app.py
└── venv/                ← created by python3 -m venv venv (not in git)
```

---

## Common Errors and How to Fix Them

**`(venv)` is not showing in the prompt**
You forgot to activate the virtual environment. Run:
```bash
source venv/bin/activate
```

**`ModuleNotFoundError: No module named 'flask'`**
Same cause — virtual environment not active. Run the command above.

**`Address already in use` when starting the app**
Port 5000 is already being used. Either stop the other process, or run Flask on a
different port:
```bash
flask run --port 5001
```
Then visit `http://127.0.0.1:5001`.

**`TemplateNotFoundError: index.html`**
Flask can't find your HTML file. Check:
1. The file is in `templates/` (not `template/` or any other name)
2. The filename matches exactly — `index.html` not `Index.html`

**`sqlite3.OperationalError: no such table: menu_items`**
The database was never initialized. This usually means `init_db()` didn't run.
You can run it manually:
```bash
python database.py
```

**`jinja2.exceptions.UndefinedError: 'X' is undefined`**
The template is trying to use a variable that wasn't passed to `render_template()`.
Check that your route passes all the variables the template expects.

**Tests fail with `no such table`**
The test fixture didn't create the schema. Make sure the `CREATE TABLE` SQL is in the
fixture before the `INSERT` statements.

---

## What to Add Next

Once you are comfortable with this project, here are the natural next steps for the capstone:

1. **User login** — add Flask-Login so only authenticated users can edit the menu
2. **PDF report** — use the `reportlab` library to export the report as a downloadable PDF
3. **Image uploads** — let users attach a photo to each item, stored in `static/uploads/`
4. **Deploy to AWS Elastic Beanstalk** — follow the video linked in the capstone tips
5. **Custom domain via Route 53** — register a `.com` and point it at your deployed app
6. **Environment variables** — move the secret key to a `.env` file using `python-dotenv`
