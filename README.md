# Gen.ke — Kenya Point of Sale & Inventory System (Django + SQLite)

Gen.ke is a scalable Point-of-Sale, inventory management, staff role management, and automated receipt system built for Kenyan businesses (**Shop**, **Retail Shop**, **Restaurant**, and **Supermarket**).

## Tech Stack
- **Backend:** Python 3.10+, Django 5.0+
- **Database:** SQLite (`db.sqlite3`)
- **Frontend:** HTML5, CSS3 (`static/css/genke.css`), Vanilla JavaScript (`static/js/pos.js`)

## Quick Start in Your IDE (VS Code / PyCharm)

1. **Create & activate a virtual environment:**
   ```bash
   python -m venv venv
   # macOS / Linux:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Seed starter Kenyan business data, products, and role accounts:**
   ```bash
   python manage.py seed_genke
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000` in your browser.

## Default Seeded Accounts (Email & Password Auth)
- **Admin:** `admin@gen.ke` / `GenkeAdmin2026!`
- **Cashier:** `cashier@gen.ke` / `GenkeCashier2026!`
- **Staff:** `staff@gen.ke` / `GenkeStaff2026!`

## Features
- Email & password authentication with Admin, Cashier, and Staff role permissions
- Customizable Business Mode (`shop`, `retail_shop`, `restaurant`, `supermarket`), KRA PIN, M-Pesa Till/Paybill, and VAT rate
- Product catalog with image upload (`Pillow`), SKU tracking, buying/selling prices, and low-stock alerts
- Interactive POS checkout with live cart, KES currency formatting, M-Pesa/Cash/Card payment capture, and automated printable receipts
- Sales reports, profit margins, and CSV export
