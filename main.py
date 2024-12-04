"""
Airline Management System - Flask Application
Expanded with user roles, insurance, promotions, and system logs.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = "airline_secret_key"  # For flash messaging

DB_NAME = "airline_management_system_final.db"


# ---------- DATABASE SETUP AND UTILITY FUNCTIONS ---------- #

def init_db():
    """Initialize the database schema."""
    with sqlite3.connect(DB_NAME) as conn:
        # Admins and Users
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT UNIQUE,
                role TEXT DEFAULT 'user'
            )
        """)
        
        # Flights and Tickets
        conn.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_number TEXT UNIQUE,
                destination TEXT,
                departure TEXT,
                price REAL,
                seats_available INTEGER,
                status TEXT DEFAULT 'On Time',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS passengers (
                passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                age INTEGER,
                passport_number TEXT UNIQUE,
                ticket_id TEXT,
                flight_id INTEGER,
                insurance BOOLEAN DEFAULT 0,
                FOREIGN KEY(flight_id) REFERENCES flights(flight_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        
        # Transactions and Logs
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                passenger_id INTEGER,
                ticket_id TEXT,
                flight_id INTEGER,
                amount REAL,
                transaction_date TEXT,
                FOREIGN KEY(passenger_id) REFERENCES passengers(passenger_id),
                FOREIGN KEY(flight_id) REFERENCES flights(flight_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                details TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Promotions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS promotions (
                promo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                discount REAL,
                expiration_date TEXT
            )
        """)

    print("Database initialized successfully.")


def execute_query(query, params=()):
    """Execute a database query."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor


def fetch_all(query, params=()):
    """Fetch all records for a query."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(query, params)
        return cursor.fetchall()


def fetch_one(query, params=()):
    """Fetch a single record for a query."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(query, params)
        return cursor.fetchone()


def log_action(user_id, action, details):
    """Log user actions in the system."""
    execute_query("""
        INSERT INTO logs (user_id, action, details)
        VALUES (?, ?, ?)
    """, (user_id, action, details))


# ---------- USER ROLES AND AUTHENTICATION ---------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    """General login route for admins and users."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = fetch_one("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        admin = fetch_one("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        
        if admin:
            session["admin_logged_in"] = True
            session["admin_id"] = admin[0]
            session["role"] = "admin"
            flash("Admin logged in successfully!", "success")
            return redirect(url_for("admin_dashboard"))
        elif user:
            session["user_logged_in"] = True
            session["user_id"] = user[0]
            session["username"] = username
            session["role"] = user[4]
            flash("User logged in successfully!", "success")
            return redirect(url_for("user_dashboard"))
        
        flash("Invalid username or password!", "danger")
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logout route."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------- PROMOTIONS AND DISCOUNTS ---------- #

@app.route("/admin/promotions", methods=["GET", "POST"])
def manage_promotions():
    """Admin route to manage promotions."""
    if session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        code = request.form["code"]
        discount = request.form["discount"]
        expiration_date = request.form["expiration_date"]
        try:
            execute_query("""
                INSERT INTO promotions (code, discount, expiration_date)
                VALUES (?, ?, ?)
            """, (code, discount, expiration_date))
            flash("Promotion added successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Promotion code already exists!", "danger")
    
    promotions = fetch_all("SELECT * FROM promotions")
    return render_template("manage_promotions.html", promotions=promotions)


@app.route("/apply_promotion", methods=["POST"])
def apply_promotion():
    """Apply a promotion to a transaction."""
    code = request.form["promo_code"]
    promotion = fetch_one("SELECT * FROM promotions WHERE code = ?", (code,))
    
    if not promotion:
        flash("Invalid promotion code!", "danger")
        return redirect(url_for("user_dashboard"))
    
    expiration_date = datetime.strptime(promotion[3], "%Y-%m-%d")
    if datetime.now() > expiration_date:
        flash("Promotion has expired!", "danger")
        return redirect(url_for("user_dashboard"))
    
    session["discount"] = promotion[2]
    flash(f"Promotion applied! Discount: {promotion[2]}%", "success")
    return redirect(url_for("user_dashboard"))


# ---------- FLIGHT INSURANCE ---------- #

@app.route("/add_insurance/<int:ticket_id>")
def add_insurance(ticket_id):
    """Add insurance to a ticket."""
    execute_query("UPDATE passengers SET insurance = 1 WHERE ticket_id = ?", (ticket_id,))
    flash("Insurance added to your ticket.", "success")
    return redirect(url_for("user_dashboard"))


# ---------- SYSTEM LOGS ---------- #

@app.route("/admin/logs")
def view_logs():
    """Admin route to view system logs."""
    if session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    logs = fetch_all("SELECT * FROM logs")
    return render_template("view_logs.html", logs=logs)

@app.route("/recommend_flights", methods=["GET", "POST"])
def recommend_flights():
    """Recommend flights based on user preferences."""
    flights = []
    if request.method == "POST":
        destination = request.form.get("destination", "").strip()
        max_price = request.form.get("max_price", "").strip()
        departure_date = request.form.get("departure_date", "").strip()

        query = "SELECT * FROM flights WHERE 1=1"
        params = []

        # Add filters dynamically based on input
        if destination:
            query += " AND destination LIKE ?"
            params.append(f"%{destination}%")
        if max_price:
            query += " AND price <= ?"
            params.append(max_price)
        if departure_date:
            query += " AND departure LIKE ?"
            params.append(f"%{departure_date}%")

        flights = fetch_all(query, params)
        if not flights:
            flash("No flights match your criteria.", "warning")
        else:
            flash(f"{len(flights)} flight(s) found!", "success")

    return render_template("recommend_flights.html", flights=flights)



# ---------- RUN APP ---------- #
if __name__ == "__main__":
    init_db()  # Initialize the database schema

    # Add default admin user if none exist
    if not fetch_one("SELECT * FROM admins"):
        execute_query("INSERT INTO admins (username, password) VALUES (?, ?)", ("admin", "admin123"))
        print("Default admin created (Username: admin, Password: admin123).")

    # Add default promotions for testing
    if not fetch_one("SELECT * FROM promotions"):
        execute_query("""
            INSERT INTO promotions (code, discount, expiration_date) 
            VALUES ('WELCOME10', 10, ?)
        """, ((datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),))
        print("Default promotion added (Code: WELCOME10, Discount: 10%).")

    # Add sample flights if none exist
    if not fetch_one("SELECT * FROM flights"):
        execute_query("""
            INSERT INTO flights (flight_number, destination, departure, price, seats_available, status) 
            VALUES 
            ('AI101', 'New York', '2024-12-15 08:00:00', 500.00, 20, 'On Time'),
            ('AI102', 'London', '2024-12-16 10:00:00', 450.00, 15, 'On Time'),
            ('AI103', 'Paris', '2024-12-17 13:00:00', 400.00, 10, 'On Time')
        """)
        print("Sample flights added to the system.")

    # Run the Flask app
    app.run(debug=True)
