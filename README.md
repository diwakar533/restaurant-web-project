# DineFlow – Restaurant Management System

DineFlow is a web-based restaurant management system designed to provide an attractive restaurant website with an online table reservation feature.

## Features

- Responsive restaurant website
- Home, About, Menu, Specials, Gallery, Reviews, Booking, and Contact sections
- Online table reservation form
- Flask backend with SQLite database
- Admin login and reservation management dashboard
- Update reservation status to Pending, Confirmed, or Cancelled
- Google Maps directions link

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite

## Project Structure

```text
DineFlow/
├── app.py
├── requirements.txt
├── README.md
└── project[1]/
    └── dIV/
        └── index.html
```

## Installation and Setup

1. Install Python on your computer.
2. Open the project folder in VS Code.
3. Create and activate a virtual environment:

   ```bash
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   py -m pip install -r requirements.txt
   ```

5. Set the required environment variables in PowerShell:

   ```powershell
   $env:ADMIN_PASSWORD = "choose-a-strong-password"
   $env:FLASK_SECRET_KEY = "replace-with-a-long-random-secret"
   ```

6. Run the application:

   ```bash
   py app.py
   ```

7. Open the website at `http://127.0.0.1:5000`.

## Admin Dashboard

Open `http://127.0.0.1:5000/admin/login` to access the admin login page. Use the password configured in your environment.

## Database

DineFlow uses SQLite to store reservation information. The database is created by the application as configured in the backend.

## Future Enhancements

- Email or SMS reservation notifications
- Table availability and capacity management
- Online payment integration
- Customer accounts and reservation history

## Disclaimer

This project is intended for educational and demonstration purposes. Configure secure credentials and production-ready settings before deploying it publicly.
