# Gold Jewellery Pledge and Interest Calculation System

A web-based application to manage gold jewellery pledge records and automatically calculate interest based on loan amount, interest rate, and number of days.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask)
- **Database:** MySQL

## Features

- Enter customer and jewellery details
- Set loan amount and customizable annual interest rate
- Choose pledge date and return date
- Automatic calculation of:
  - Total number of days
  - Per-day interest
  - Total interest
  - Final payable amount
- Save, view, edit, and delete pledge records

## Interest Formula

The system uses an annual interest rate divided over 365 days:

```
Per-day interest = (Loan Amount × Interest Rate / 100) / 365
Total interest   = Per-day interest × Total days
Final amount     = Loan Amount + Total interest
```

**Example:** Loan of ₹50,000 at 7% for 30 days

- Per-day interest = (50000 × 7 / 100) / 365 = ₹9.5890
- Total interest = ₹9.5890 × 30 = ₹287.67
- Final amount = ₹50,287.67

## Setup Instructions (AMPPS)

### 1. Create the database

1. Start **AMPPS** and ensure **MySQL** is running.
2. Open **phpMyAdmin** or MySQL command line.
3. Import or run the SQL file:

```sql
SOURCE "C:/Program Files/Ampps/www/interest/database.sql";
```

### 2. Configure database connection

Edit `config.py` if your MySQL credentials differ from the AMPPS defaults:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",
    "database": "gold_pledge_db",
    "port": 3306,
}
```

### 3. Install Python dependencies

Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Open your browser and visit:

```
http://localhost:5000
```

## Project Structure

```
interest/
├── app.py                 # Flask backend and API routes
├── config.py              # Database configuration
├── database.sql           # MySQL schema
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Main page
└── static/
    ├── css/style.css
    └── js/app.js
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web interface |
| POST | `/api/calculate` | Calculate interest without saving |
| GET | `/api/pledges` | List all pledge records |
| POST | `/api/pledges` | Create a new pledge |
| GET | `/api/pledges/<id>` | Get a single pledge |
| PUT | `/api/pledges/<id>` | Update a pledge |
| DELETE | `/api/pledges/<id>` | Delete a pledge |
