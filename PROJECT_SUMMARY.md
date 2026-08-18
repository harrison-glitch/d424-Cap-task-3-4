# Restaurant Menu Manager — Project Summary Script

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

**Step 1 — Create the project folder.**
Using the macOS Terminal, the main project directory and three subdirectories were created: `templates` for HTML files, `static/css` for the stylesheet, and `tests` for the test suite. This gives Flask the exact folder structure it expects.

**Step 2 — Set up a virtual environment.**
An isolated Python environment was created using `python3 -m venv venv` and activated with `source venv/bin/activate`. This keeps the project's packages separate from everything else on the system, which is standard practice for every Python project.

**Step 3 — Install dependencies.**
A `requirements.txt` file was created pinning Flask and pytest to exact versions, then installed with `pip install -r requirements.txt`. Pinning versions ensures anyone who clones the project gets the exact same setup.

**Step 4 — Create database.py.**
This file handles all database logic. It defines the path to the SQLite file, a `get_connection` function that opens the database and enables column-name access on rows, and an `init_db` function that creates the menu items table and seeds ten sample items on first run. Parameterized queries are used throughout to prevent SQL injection.

**Step 5 — Create app.py.**
This is the core of the application. The Flask app is configured with logging and eight route functions — one for each URL the app responds to. The index route loads and optionally filters all menu items. The add, edit, and delete routes handle full CRUD operations with input validation. The toggle route flips an item's availability. The report route calculates summary statistics and groups items by category before passing everything to the template.

**Step 6 — Create the HTML templates.**
Five HTML files live in the `templates` folder. A base template defines the shared layout — the navigation bar, flash message display, and footer. The four page templates each extend the base and fill in their own content. Jinja2 syntax handles dynamic output, loops over database rows, conditional styling, and form generation.

**Step 7 — Create the stylesheet.**
A single CSS file in `static/css` handles all visual styling. It uses a system font stack for a native look on every platform, a composable button class system, color-coded category badges that connect directly to Jinja2 template logic, and a flexbox layout for the report summary cards.

**Step 8 — Write the tests.**
A pytest test file covers all thirteen test cases across every route. A fixture function creates a temporary database file before each test and deletes it after, ensuring tests are fully isolated. Tests verify page loads, category filtering, valid form submissions, input validation errors, item deletion, availability toggling, and report generation.

**Step 9 — Run the app.**
With the virtual environment active, running `python app.py` starts the Flask development server. The app is accessible at `http://127.0.0.1:5000` in any browser. The database is created and seeded automatically on first run.

**Step 10 — Run the tests.**
Running `python -m pytest tests/ -v` executes all thirteen tests. The `-v` flag shows each test name and result individually. All thirteen pass.

**Step 11 — Create .gitignore.**
A `.gitignore` file tells Git to exclude the virtual environment folder, compiled Python files, the database file, and macOS system files. These are environment-specific and should never be committed to version control.

**Step 12 — Push to GitHub.**
Using Git and the GitHub CLI, a repository was initialized, all project files were staged and committed with a descriptive message, and everything was pushed to a new public repository named `d424 Cap task 3-4`.

---

## Result

The completed application demonstrates full CRUD functionality, input validation, error handling, structured logging, automated testing, and a report generation feature — all core requirements for the WGU D424 Software Engineering Capstone. The codebase is fully documented, tested, and version controlled on GitHub at:

**https://github.com/harrison-glitch/d424-Cap-task-3-4**
