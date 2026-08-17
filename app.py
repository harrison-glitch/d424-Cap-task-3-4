"""
app.py - Main Flask application for Restaurant Menu Manager.

Routes:
    GET  /                  - View all menu items (with optional category filter)
    GET  /add               - Show add item form
    POST /add               - Submit new menu item
    GET  /edit/<id>         - Show edit form for an item
    POST /edit/<id>         - Submit edits for an item
    POST /delete/<id>       - Delete a menu item
    POST /toggle/<id>       - Toggle item availability on/off
    GET  /report            - View menu summary report
"""

import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db

# --- App setup ---
app = Flask(__name__)
app.secret_key = "restaurant-menu-secret-key"  # required for flash messages

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

CATEGORIES = ["Appetizer", "Main", "Dessert", "Drink"]


# --- Routes ---

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


@app.route("/add", methods=["GET", "POST"])
def add_item():
    """Add a new menu item."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()
        available = 1 if request.form.get("available") else 0

        # Input validation
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
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()
        available = 1 if request.form.get("available") else 0

        # Input validation
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
            return render_template("edit.html", item=item, categories=CATEGORIES)

        try:
            conn = get_connection()
            conn.execute(
                "UPDATE menu_items SET name=?, category=?, description=?, price=?, available=? WHERE id=?",
                (name, category, description, price, available, item_id)
            )
            conn.commit()
            conn.close()
            logger.info("Updated menu item id=%d: %s", item_id, name)
            flash(f"'{name}' updated successfully!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            logger.error("Failed to update item %d: %s", item_id, e)
            flash("Error updating item. Please try again.", "danger")

    return render_template("edit.html", item=item, categories=CATEGORIES)


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    """Delete a menu item by ID."""
    try:
        conn = get_connection()
        item = conn.execute("SELECT name FROM menu_items WHERE id = ?", (item_id,)).fetchone()
        if item:
            conn.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
            conn.commit()
            logger.info("Deleted menu item id=%d: %s", item_id, item["name"])
            flash(f"'{item['name']}' deleted.", "success")
        else:
            flash("Item not found.", "danger")
        conn.close()
    except Exception as e:
        logger.error("Failed to delete item %d: %s", item_id, e)
        flash("Error deleting item.", "danger")

    return redirect(url_for("index"))


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
            logger.info("Toggled item id=%d '%s' to %s", item_id, item["name"], status_label)
            flash(f"'{item['name']}' marked as {status_label}.", "success")
        else:
            flash("Item not found.", "danger")
        conn.close()
    except Exception as e:
        logger.error("Failed to toggle item %d: %s", item_id, e)
        flash("Error updating availability.", "danger")

    return redirect(url_for("index"))


@app.route("/report")
def report():
    """Generate a summary report of the menu."""
    try:
        conn = get_connection()
        all_items = conn.execute("SELECT * FROM menu_items ORDER BY category, name").fetchall()

        # Build report data by category
        report_data = {}
        for item in all_items:
            cat = item["category"]
            if cat not in report_data:
                report_data[cat] = {"menu_items": [], "total": 0, "available": 0}
            report_data[cat]["menu_items"].append(item)
            report_data[cat]["total"] += 1
            if item["available"]:
                report_data[cat]["available"] += 1

        # Overall stats
        total_items = len(all_items)
        total_available = sum(1 for i in all_items if i["available"])
        prices = [i["price"] for i in all_items]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        conn.close()
        logger.info("Generated menu report: %d total items", total_items)
    except Exception as e:
        logger.error("Failed to generate report: %s", e)
        flash("Error generating report.", "danger")
        return redirect(url_for("index"))

    return render_template(
        "report.html",
        report_data=report_data,
        total_items=total_items,
        total_available=total_available,
        avg_price=avg_price,
        min_price=min_price,
        max_price=max_price
    )


# --- Entry point ---
if __name__ == "__main__":
    init_db()
    logger.info("Starting Restaurant Menu Manager...")
    app.run(debug=True)
