# DineFlow — Restaurant Management System

DineFlow is a beginner-friendly restaurant reservation project built with technologies you can explain: HTML, CSS, JavaScript, Python Flask, and SQLite.

## What the project does
1. Shows a restaurant website with Home, About, Menu, Specials, Gallery, Reviews, Booking, and Contact sections.
2. Lets a customer submit a table reservation with restaurant name, customer name, phone number, email, date, time, and number of guests.
3. Uses Flask to validate the request on the server.
4. Saves the reservation in the local SQLite database `dineflow.db` with `Pending` status.
5. Provides a password-protected admin dashboard to view bookings and update their status to Pending, Confirmed, or Cancelled.

## Technology stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python and Flask
- Database: SQLite

## Run on Windows
Open the `DineFlow` folder in VS Code. Open the terminal in the folder that contains `app.py`, then run:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
$env:ADMIN_PASSWORD = "choose-a-strong-password"
$env:FLASK_SECRET_KEY = "replace-with-a-long-random-secret"
py app.py
```

Open http://127.0.0.1:5000

## Admin dashboard
Open http://127.0.0.1:5000/admin/login and enter the password you set in `ADMIN_PASSWORD` before starting Flask.

## Main backend routes
- `GET /` — serves the website
- `GET /api/health` — checks whether the backend is running
- `POST /api/reservations` — validates and saves a booking
- `GET /admin/login` — admin sign-in
- `GET /admin` — reservation dashboard
- `POST /admin` — updates a reservation status

## How to explain it in an interview
“When a customer submits the booking form, JavaScript sends the form data to a Flask API using a POST request. Flask validates the fields and inserts the reservation into SQLite using a parameterized SQL query. The admin dashboard reads saved reservations and lets an administrator update the booking status.”

## Important
- This is a learning/demo project. It does not check live table capacity or send confirmation messages by email/SMS.
- The menu, sample reviews, opening hours, and Google Maps search link are demo content. Update them before presenting the project as a real restaurant's live website.
- The hero and food photos are loaded from remote image URLs, so an internet connection is needed for those images.
- Do not expose Flask's built-in development server to the public internet.
