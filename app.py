import os
import re
import sqlite3
from datetime import date, datetime
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, session, redirect, url_for, render_template_string

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "project[1]", "dIV")
DATABASE_PATH = os.path.join(BASE_DIR, "dineflow.db")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-development-secret")


def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, restaurant_name TEXT NOT NULL DEFAULT 'DineFlow', name TEXT NOT NULL, address TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL, phone TEXT NOT NULL, reservation_date TEXT NOT NULL, reservation_time TEXT NOT NULL,
            guests INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'Pending', created_at TEXT NOT NULL)""")
        # Upgrade an existing database created by an earlier DineFlow version.
        columns = {row["name"] for row in db.execute("PRAGMA table_info(reservations)").fetchall()}
        if "address" not in columns:
            db.execute("ALTER TABLE reservations ADD COLUMN address TEXT NOT NULL DEFAULT ''")
        if "restaurant_name" not in columns:
            db.execute("ALTER TABLE reservations ADD COLUMN restaurant_name TEXT NOT NULL DEFAULT 'DineFlow'")


def clean(value, limit=254):
    return value.strip()[:limit] if isinstance(value, str) else ""


def valid_email(value):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value))


@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify(status="ok", message="DineFlow backend is running")


@app.post("/api/reservations")
def create_reservation():
    data = request.get_json(silent=True) or {}
    restaurant_name = clean(data.get("restaurant_name"), 100) or "DineFlow"
    if restaurant_name != "DineFlow":
        return jsonify(error="Restaurant name must be DineFlow."), 400
    name = clean(data.get("name"), 100)
    address = clean(data.get("address"), 250)
    email = clean(data.get("email")).lower()
    phone = clean(data.get("phone"), 20)
    day = clean(data.get("date"), 10)
    time = clean(data.get("time"), 5)
    guests_text = clean(str(data.get("guests", "")), 2)
    if not all([name, email, phone, day, time, guests_text]):
        return jsonify(error="Please complete all reservation fields."), 400
    if not valid_email(email):
        return jsonify(error="Please enter a valid email address."), 400
    if not re.fullmatch(r"[+0-9() -]{7,20}", phone):
        return jsonify(error="Please enter a valid phone number."), 400
    try:
        chosen_day = date.fromisoformat(day)
        guests = int(guests_text)
    except (ValueError, TypeError):
        return jsonify(error="Please enter a valid date and number of guests."), 400
    if chosen_day < date.today():
        return jsonify(error="Reservation date cannot be in the past."), 400
    if time not in {"17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00"}:
        return jsonify(error="Please choose one of the listed reservation times."), 400
    if not 1 <= guests <= 8:
        return jsonify(error="Guest count must be between 1 and 8."), 400
    with get_db() as db:
        cursor = db.execute("""INSERT INTO reservations
            (restaurant_name,name,address,email,phone,reservation_date,reservation_time,guests,status,created_at)
            VALUES (?,?,?,?,?,?,?,?,'Pending',?)""",
            (restaurant_name, name, address, email, phone, day, time, guests, datetime.now().isoformat(timespec="seconds")))
        reservation_id = cursor.lastrowid
    return jsonify(message=f"Thank you, {name}! Your reservation request has been saved. Our team will confirm it.",
                   reservation_id=reservation_id), 201



def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    configured_password = os.environ.get("ADMIN_PASSWORD")
    error = ""
    if request.method == "POST":
        if not configured_password:
            error = "Set the ADMIN_PASSWORD environment variable before using the dashboard."
        elif request.form.get("password", "") == configured_password:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Incorrect password."
    return render_template_string("""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DineFlow Admin</title>
    <style>body{font-family:Arial;background:#171717;color:#f5f0e6;display:grid;place-items:center;min-height:100vh;margin:0}form{background:#242424;padding:2rem;border-radius:14px;width:min(340px,85vw)}h1{color:#d4af37}input,button{box-sizing:border-box;width:100%;padding:12px;margin-top:12px;border-radius:7px}button{background:#d4af37;border:0;font-weight:bold}.error{color:#ffb4a9}</style></head>
    <body><form method="post"><h1>DineFlow Admin</h1><p>Sign in to manage reservations.</p><input type="password" name="password" placeholder="Admin password" required><button>Sign in</button><p class="error">{{ error }}</p></form></body></html>""", error=error)


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_dashboard():
    if request.method == "POST":
        try:
            reservation_id = int(request.form.get("reservation_id", ""))
        except ValueError:
            return redirect(url_for("admin_dashboard"))
        status = request.form.get("status", "")
        if status in {"Pending", "Confirmed", "Cancelled"}:
            with get_db() as db:
                db.execute("UPDATE reservations SET status=? WHERE id=?", (status, reservation_id))
        return redirect(url_for("admin_dashboard"))
    with get_db() as db:
        reservations = db.execute("SELECT * FROM reservations ORDER BY id DESC").fetchall()
    return render_template_string("""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DineFlow Admin Dashboard</title>
    <style>*{box-sizing:border-box}body{font-family:Arial;background:#f6f4ef;color:#222;margin:0;padding:24px}header{display:flex;justify-content:space-between;flex-wrap:wrap}h1{color:#8a6b12}a{color:#8a6b12}section{background:white;border-radius:12px;padding:18px;margin:18px 0;overflow:auto}table{border-collapse:collapse;width:100%;min-width:760px}th,td{text-align:left;padding:10px;border-bottom:1px solid #eee;font-size:14px}th{background:#f3eee0}select,button{padding:8px;border-radius:6px;border:1px solid #ccc}button{background:#d4af37;border:0;cursor:pointer}</style></head><body>
    <header><div><h1>DineFlow Admin Dashboard</h1><p>Review booking requests and update reservation status.</p></div><a href="/admin/logout">Log out</a></header>
    <section><h2>Reservations ({{ reservations|length }})</h2>{% if reservations %}<table><tr><th>ID</th><th>Restaurant</th><th>Name</th><th>Email</th><th>Phone</th><th>Date</th><th>Time</th><th>Guests</th><th>Status</th><th>Update</th></tr>
    {% for r in reservations %}<tr><td>{{r['id']}}</td><td>{{r['restaurant_name']}}</td><td>{{r['name']}}</td><td>{{r['email']}}</td><td>{{r['phone']}}</td><td>{{r['reservation_date']}}</td><td>{{r['reservation_time']}}</td><td>{{r['guests']}}</td><td>{{r['status']}}</td><td><form method="post"><input type="hidden" name="reservation_id" value="{{r['id']}}"><select name="status">{% for s in ['Pending','Confirmed','Cancelled'] %}<option {% if s==r['status'] %}selected{% endif %}>{{s}}</option>{% endfor %}</select> <button>Save</button></form></td></tr>{% endfor %}</table>{% else %}<p>No reservations yet. Submit a test booking from the website.</p>{% endif %}</section>
    </body></html>""",
        reservations=reservations)


if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
