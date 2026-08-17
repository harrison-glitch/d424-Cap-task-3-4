# How to Build the Restaurant Menu Manager — Step by Step

This guide walks you through building this project from scratch, explaining every file,
every section of code, and why each decision was made. Written for someone early in their
CS degree who is comfortable with basic Python but new to web apps.

---

## What We're Building

A web application that lets you manage a restaurant's menu in a browser. You can:
- See all menu items in a table
- Add, edit, and delete items
- Mark items as available or unavailable
- View a report summarizing the menu

---

## The Tech Stack (and Why)

| Tool | What it does | Why we use it |
|------|-------------|---------------|
| **Python** | Programming language | You already know it |
| **Flask** | Web framework | Lightweight, beginner-friendly, runs a local web server |
| **SQLite** | Database | Built into Python, no server setup needed, perfect for small apps |
| **Jinja2** | HTML templating | Comes with Flask, lets you put Python variables inside HTML |
| **pytest** | Testing framework | Standard Python testing tool |

---

## Prerequisites

Before starting, make sure you have:
- Python 3.9 or newer installed (`python3 --version` to check)
- A terminal (Terminal on Mac, Command Prompt or PowerShell on Windows)
- A code editor (VS Code recommended)
- Git installed (`git --version` to check)
- A GitHub account

---

## Step 1 — Create the Project Folder

Open your terminal and run:

```bash
mkdir restaurant-menu
cd restaurant-menu
mkdir templates
mkdir -p static/css
mkdir tests
```

**What this does:**
- `mkdir restaurant-menu` — creates the project folder
- `cd restaurant-menu` — moves into it
- `mkdir templates` — Flask looks here for your HTML files
- `mkdir -p static/css` — Flask looks here for CSS, images, etc. The `-p` flag creates both `static/` and `css/` at once
- `mkdir tests` — where your test files go

Your folder should now look like this:
```
restaurant-menu/
├── templates/
├── static/
│   └── css/
└── tests/
```

---

## Step 2 — Set Up a Virtual Environment

A virtual environment is an isolated box for your Python packages. It keeps this project's
dependencies separate from everything else on your computer.

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

You'll know it worked when you see `(venv)` at the start of your terminal prompt.

**Why this matters:** Without a virtual environment, every Python project on your computer
shares the same packages. That causes version conflicts. Always use one per project.

---

## Step 3 — Install Dependencies

Create a file called `requirements.txt` in your project root:

```
Flask==3.0.3
pytest==8.3.2
```

Then install them:

```bash
pip install -r requirements.txt
```

**What each package does:**
- `Flask` — the web framework that handles URLs, requests, and responses
- `pytest` — the testing framework we'll use later

**Why pin exact versions?** Writing `Flask==3.0.3` instead of just `Flask` means anyone
who clones your project gets the exact same version you used. This prevents "it works on
my machine" problems.

---

## Step 4 — Create the Database File (`database.py`)

Create `database.py` in the project root. This file handles everything related to the
database — connecting to it and setting it up.

```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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

    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_items = [
            ("Mozzarella Sticks", "Appetizer", "Fried mozzarella with marinara sauce", 8.99, 1),
            ("Cheeseburger", "Main", "8oz beef patty with cheddar, lettuce, tomato", 13.99, 1),
            ("Chocolate Lava Cake", "Dessert", "Warm chocolate cake with vanilla ice cream", 7.99, 1),
            ("Lemonade", "Drink", "Fresh squeezed lemonade", 3.49, 1),
        ]
        cursor.executemany(
            "INSERT INTO menu_items (name, category, description, price, available) VALUES (?, ?, ?, ?, ?)",
            sample_items
        )

    conn.commit()
    conn.close()
```

### Breaking it down:

**`DB_PATH`**
```python
DB_PATH = os.path.join(os.path.dirname(__file__), "menu.db")
```
This builds an absolute path to `menu.db` in the same folder as `database.py`.
`__file__` is Python's built-in variable that holds the current file's path.
`os.path.dirname()` gets just the folder part of that path.
`os.path.join()` combines them cleanly, whether you're on Mac, Windows, or Linux.

**`get_connection()`**
```python
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
return conn
```
`sqlite3.connect()` opens the database file (or creates it if it doesn't exist).
`conn.row_factory = sqlite3.Row` is important — without it, database rows come back as
plain tuples and you'd access data by index like `row[0]`. With it, you can access data
by column name like `row["name"]`, which is much more readable.

**`init_db()`**
The `CREATE TABLE IF NOT EXISTS` line creates the table only if it doesn't already exist.
This means you can safely call `init_db()` every time the app starts without destroying
your data.

The `?` placeholders in the INSERT statement are parameterized queries. This is a security
practice — never put variables directly into SQL strings, or you open yourself up to
SQL injection attacks.

**The table columns:**
- `id` — auto-incremented unique number for each row
- `name` — the item's name (required)
- `category` — Appetizer, Main, Dessert, or Drink (required)
- `description` — optional description
- `price` — stored as `REAL` (a decimal number)
- `available` — stored as `INTEGER` (0 = unavailable, 1 = available). SQLite has no
  true boolean type, so we use 0 and 1.

---

## Step 5 — Create the Flask App (`app.py`)

This is the heart of the project. Create `app.py` in the project root.

### 5a — App Setup

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

**`Flask(__name__)`** — Creates the Flask app. `__name__` tells Flask where to look for
templates and static files relative to this file.

**`app.secret_key`** — Required for flash messages (the little success/error banners).
Flask uses this to sign the session cookie. In a real production app you'd load this from
an environment variable, not hardcode it.

**`logging.basicConfig()`** — Sets up Python's built-in logger so every log line includes
a timestamp and the log level (INFO, ERROR, etc.). This is how you see what the app is
doing without adding print statements everywhere.

**`CATEGORIES`** — A list defined once at the top so you never have to type it out in
multiple places. If you add a category later, you change it in one spot.

---

### 5b — The Index Route (View All Items)

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

    return render_template("index.html", items=items, categories=CATEGORIES,
                           selected_category=category_filter)
```

**`@app.route("/")`** — This decorator tells Flask: "when someone visits the homepage,
run the `index()` function below."

**`request.args.get("category", "")`** — `request.args` contains URL query parameters.
If the URL is `/?category=Main`, this gets `"Main"`. The `""` is the default if no
category is in the URL.

**`try/except`** — Any database error is caught, logged, and a friendly message is shown
to the user instead of a crash page. The `items = []` fallback means the page still
renders, just empty.

**`render_template()`** — Tells Flask to find `templates/index.html` and fill in the
variables you're passing. `items=items` makes the Python `items` list available inside
the HTML as `{{ items }}`.

---

### 5c — The Add Route

```python
@app.route("/add", methods=["GET", "POST"])
def add_item():
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

        conn = get_connection()
        conn.execute(
            "INSERT INTO menu_items (name, category, description, price, available) VALUES (?, ?, ?, ?, ?)",
            (name, category, description, price, available)
        )
        conn.commit()
        conn.close()
        flash(f"'{name}' added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add.html", categories=CATEGORIES, form_data={})
```

**`methods=["GET", "POST"]`** — By default Flask routes only accept GET requests. You
have to explicitly allow POST for form submissions.

**`if request.method == "POST"`** — The same URL handles two situations:
- GET: show the empty form
- POST: process the submitted form data

**`.strip()`** — Removes accidental leading/trailing spaces from user input.

**`available = 1 if request.form.get("available") else 0`** — Checkboxes in HTML only
appear in form data when checked. If the checkbox is unchecked, `request.form.get("available")`
returns `None`, so this becomes `0`. If checked, it returns `"on"`, which is truthy, so
this becomes `1`.

**Validation** — Before touching the database, we check that the data makes sense.
This prevents garbage data from getting saved and protects against basic misuse.

**`redirect(url_for("index"))`** — After successfully saving, we redirect the user back
to the homepage. `url_for("index")` generates the URL for the `index` function, which is `"/"`.
This is better than hardcoding `"/"` because if you ever change the route, it updates automatically.

---

### 5d — Edit, Delete, and Toggle Routes

These follow the same pattern as Add. Key points:

**Edit** (`/edit/<int:item_id>`):
- The `<int:item_id>` in the route is a URL variable. Flask automatically extracts the
  number from the URL and passes it to the function.
- On GET: load the item from the database, pre-fill the form with its current values
- On POST: validate, then run `UPDATE` SQL

**Delete** (`/delete/<int:item_id>`):
- Only accepts POST (you don't want someone able to delete items just by visiting a URL)
- Runs `DELETE FROM menu_items WHERE id = ?`
- Redirects back to the homepage

**Toggle** (`/toggle/<int:item_id>`):
- Reads the current `available` value
- Flips it: `new_status = 0 if item["available"] else 1`
- Runs `UPDATE` to save the new value

---

### 5e — The Report Route

```python
@app.route("/report")
def report():
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

    return render_template("report.html", report_data=report_data,
                           total_items=total_items, total_available=total_available,
                           avg_price=avg_price, min_price=min_price, max_price=max_price)
```

This route fetches all items and builds a summary in Python before sending it to the
template. The `report_data` dictionary groups items by category so the template can
loop through them easily.

**`sum(1 for i in all_items if i["available"])`** — This is a generator expression.
It counts how many items have `available == 1`. It's the same as writing a for loop
that increments a counter, just more concise.

---

### 5f — Entry Point

```python
if __name__ == "__main__":
    init_db()
    logger.info("Starting Restaurant Menu Manager...")
    app.run(debug=True)
```

`if __name__ == "__main__"` — This block only runs when you execute `python app.py`
directly. It won't run when the file is imported by tests or other modules.

`init_db()` — Creates the database and seeds sample data if it doesn't exist yet.

`debug=True` — In debug mode, Flask automatically reloads when you save a file, and
shows detailed error pages. Never use this in production.

---

## Step 6 — Create the HTML Templates

Flask uses **Jinja2** to combine HTML with Python data. The `{{ variable }}` syntax
outputs a variable. The `{% for %}` and `{% if %}` syntax runs logic.

### 6a — Base Template (`templates/base.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
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
        <p>Restaurant Menu Manager — WGU Software Engineering Capstone</p>
    </footer>
</body>
</html>
```

This is the shared layout every other page inherits. It has the nav bar, the flash
message display, and a `{% block content %}` placeholder that child templates fill in.

**`{% block title %}`** — Child templates can override the page title by defining their
own `{% block title %}` block.

**`url_for('static', filename='css/style.css')`** — Generates the correct URL for your
CSS file. Using `url_for` instead of hardcoding paths means it works regardless of
where your app is deployed.

**Flash messages** — `get_flashed_messages(with_categories=true)` retrieves any messages
set by `flash()` in your routes. The `category` (success, danger) maps to CSS classes
for green/red styling.

### 6b — Other Templates

Each of the other templates (`index.html`, `add.html`, `edit.html`, `report.html`)
starts with:

```html
{% extends "base.html" %}
{% block content %}
  ... page-specific HTML here ...
{% endblock %}
```

`{% extends "base.html" %}` tells Jinja2 to use `base.html` as the wrapper and inject
this template's content into the `{% block content %}` section.

**Key Jinja2 patterns used:**

Looping over items:
```html
{% for item in items %}
  <tr>
    <td>{{ item.name }}</td>
    <td>${{ "%.2f" | format(item.price) }}</td>
  </tr>
{% endfor %}
```

Conditional styling:
```html
{% if item.available %}
  <span class="status-available">Available</span>
{% else %}
  <span class="status-unavailable">Unavailable</span>
{% endif %}
```

Form that submits a POST request:
```html
<form action="{{ url_for('delete_item', item_id=item.id) }}" method="POST">
    <button type="submit">Delete</button>
</form>
```

Note: browsers only support GET and POST natively. Flask handles routing to the right
function based on both the URL and the method.

---

## Step 7 — Create the Stylesheet (`static/css/style.css`)

The CSS file handles all visual styling. Key sections:

**Layout:**
```css
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f5f5;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
```
`-apple-system` uses the system font on Mac/iOS, `BlinkMacSystemFont` on Chrome/Mac,
and falls back to `Segoe UI` (Windows) then `Roboto` (Android/Linux). This means the
app looks native on every platform without loading a font file.

**Buttons:**
```css
.btn { display: inline-block; padding: 0.5rem 1rem; border-radius: 5px; ... }
.btn-primary   { background: #3498db; color: white; }
.btn-danger    { background: #e74c3c; color: white; }
```
A base `.btn` class with modifier classes like `.btn-primary` and `.btn-danger`.
This pattern (called BEM-style) keeps styles composable — you stack classes instead
of creating a new class for every variation.

**Category badges:**
```css
.badge-appetizer { background: #9b59b6; }
.badge-main      { background: #e67e22; }
.badge-dessert   { background: #e91e8c; }
.badge-drink     { background: #1abc9c; }
```
In the template, `{{ item.category | lower }}` converts "Appetizer" to "appetizer",
so `badge-{{ item.category | lower }}` becomes `badge-appetizer`, matching the CSS class.

---

## Step 8 — Write Tests (`tests/test_app.py`)

```python
import pytest
import os
import tempfile
import database

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    database.DB_PATH = db_path

    from app import app as flask_app
    flask_app.config["TESTING"] = True

    conn = database.get_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS menu_items (...)""")
    conn.execute("INSERT INTO menu_items ... VALUES (?, ...)", ("Test Burger", ...))
    conn.commit()
    conn.close()

    with flask_app.test_client() as test_client:
        yield test_client

    database.DB_PATH = original_path
    os.unlink(db_path)
```

**What is a fixture?**
A pytest fixture is a function that sets something up before a test and tears it down
after. The `yield` is the handoff point — code before `yield` is setup, code after is
teardown.

**Why a temp file database instead of `:memory:`?**
SQLite's `:memory:` database lives inside a single connection. When your app opens a
new connection (which it does for every request), it gets a brand new empty database.
A temp file persists across connections while still being deleted after the test.

**`flask_app.config["TESTING"] = True`** — Puts Flask into test mode, which disables
error catching so test failures show real exceptions instead of generic HTTP 500 errors.

**Example test:**
```python
def test_add_item_post_valid(client):
    response = client.post("/add", data={
        "name": "New Pizza",
        "category": "Main",
        "price": "11.99",
        "available": "on"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"New Pizza" in response.data
```

`client.post()` simulates submitting a form.
`follow_redirects=True` tells the test client to follow any redirects automatically.
`response.data` is the raw HTML bytes of the response.
`b"New Pizza"` — the `b` prefix makes it a bytes literal, which is how Flask returns
HTML.

---

## Step 9 — Run the App

```bash
source venv/bin/activate   # if not already active
python app.py
```

Open your browser to **http://127.0.0.1:5000**

Flask will print something like:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

To stop the server, press `Ctrl+C`.

---

## Step 10 — Run the Tests

```bash
python -m pytest tests/ -v
```

The `-v` flag shows each test name and whether it passed or failed. You should see
13 passed.

---

## Step 11 — Push to GitHub

```bash
# Initialize git in the project folder
git init

# Create a .gitignore so venv and the database file don't get committed
echo "venv/\n__pycache__/\n*.db\n*.pyc\n.DS_Store" > .gitignore

# Stage all files
git add .

# Make your first commit
git commit -m "feat: initial Restaurant Menu Manager"

# Create the repo on GitHub and push (requires GitHub CLI)
gh repo create "your-repo-name" --public --source . --push
```

If you don't have the GitHub CLI, go to github.com, create a new repository manually,
then run:
```bash
git remote add origin https://github.com/YOUR_USERNAME/your-repo-name.git
git push -u origin main
```

---

## Full File List

```
restaurant-menu/
├── app.py                  ← Flask app and all routes
├── database.py             ← Database connection and initialization
├── requirements.txt        ← Python packages
├── README.md               ← Project overview
├── HOW_TO_BUILD.md         ← This file
├── .gitignore              ← Files git should ignore
├── templates/
│   ├── base.html           ← Shared layout (nav, flash messages, footer)
│   ├── index.html          ← Menu list page
│   ├── add.html            ← Add item form
│   ├── edit.html           ← Edit item form
│   └── report.html         ← Report summary page
├── static/
│   └── css/
│       └── style.css       ← All styling
└── tests/
    └── test_app.py         ← 13 pytest tests
```

---

## Common Errors and Fixes

**`ModuleNotFoundError: No module named 'flask'`**
You're not in the virtual environment. Run `source venv/bin/activate` first.

**`Address already in use`**
Something else is running on port 5000. Either stop that process or run Flask on a
different port: `app.run(debug=True, port=5001)`

**`TemplateNotFoundError`**
Flask can't find your HTML file. Make sure the file is inside the `templates/` folder
and the name matches exactly (case sensitive).

**`sqlite3.OperationalError: no such table`**
The database hasn't been initialized. Make sure `init_db()` is called before the app
handles requests. It's called in the `if __name__ == "__main__"` block in `app.py`.

---

## What to Add Next (for the Real Capstone)

1. **User authentication** — Login page so not just anyone can edit the menu
2. **PDF report export** — Use the `reportlab` or `weasyprint` library
3. **Image uploads** — Let users attach a photo to each menu item
4. **Deploy to AWS Elastic Beanstalk** — Follow the videos linked in the capstone tips
5. **Custom domain via Route 53** — Register a `.com` and point it at your app
