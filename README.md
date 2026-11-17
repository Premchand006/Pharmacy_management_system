# Pharmacy Management System

A Flask app for running a pharmacy counter: stock by batch, expiry
tracking, sales, staff records and customer prescriptions.

Staff sign in to the admin portal. Customers sign in with their customer
ID and a password to view and submit prescriptions.

## Features

### Admin portal

- Employees, products and customers: add, edit, delete
- Sales grouped by product and supplier
- Reports: current stock, batches expiring within 30 days, top 10
  sellers, and batch → sale → prescription traceability
- Dashboard warning when stocked batches are about to expire

### Customer portal

- List of the customer's own prescriptions with their items
- Form to submit a new prescription

## Stack

Flask 3, Flask-SQLAlchemy, Flask-WTF (CSRF), Bootstrap 5.3. SQLite for
local use, Postgres in production.

## Run locally

Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>. On first start the app creates
`instance/pharmacy.db` and loads demo data. To wipe and reload it, run
`python seed_data.py`.

Demo logins:

| Portal   | Login              | Password      |
|----------|--------------------|---------------|
| Admin    | `admin`            | `admin123`    |
| Customer | customer ID `1`–`8`| `password123` |

Change or remove these accounts before using real data.

## Configuration

Settings come from environment variables. See `.env.example`.

| Variable         | Required        | Purpose |
|------------------|-----------------|---------|
| `SECRET_KEY`     | Yes, in production | Signs session cookies and CSRF tokens. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"`. Locally a random key is used if unset, so sessions reset on restart. |
| `DATABASE_URL`   | Yes, in production | SQLAlchemy URL, e.g. a Neon or Supabase Postgres URL. `postgres://` is accepted. |
| `SEED_DEMO_DATA` | No              | `1` loads demo data into an empty database, `0` never does. Defaults to on for SQLite and off otherwise. |
| `FLASK_DEBUG`    | No              | `1` turns on the debugger for `python app.py`. Never set it in production. |

## Deploy to Vercel

Vercel finds the Flask `app` in `app.py` on its own; no `vercel.json` is
needed. Files in `public/` are served from the CDN, so the CSS and JS
live in `public/static/`.

1. Create a Postgres database (Vercel Marketplace → Neon works) and
   copy its connection string.
2. Import the repository in Vercel.
3. Under **Settings → Environment Variables** add `SECRET_KEY` and
   `DATABASE_URL`. Add `SEED_DEMO_DATA=1` for the first deploy if you
   want the demo data, then remove it.
4. Deploy. `/healthz` returns `{"status": "ok"}` when the app is up.

Without `DATABASE_URL` the app still starts on Vercel, using SQLite in
`/tmp` with demo data. That copy is lost whenever the function cold
starts, so use it only for previews.

Or from the CLI:

```bash
npm i -g vercel
vercel env add SECRET_KEY
vercel env add DATABASE_URL
vercel --prod
```

## Project layout

```text
app.py              Flask app, config, error handlers
extensions.py       SQLAlchemy instance
models/             Database models (10 tables)
routes/             auth, admin and customer blueprints
templates/          Jinja templates
public/static/      CSS and JS (served by Vercel's CDN)
seed_data.py        Demo data
USER_GUIDE.md       Walkthrough for staff and customers
```

## Database

| Table                | Holds |
|----------------------|-------|
| `customers`          | Contact details and portal password hash |
| `employees`          | Staff, role, shift, optional login |
| `suppliers`          | Firm, GST number, drug licence, bank details |
| `products`           | Medicine, form, strength, MRP, prescription type |
| `batches`            | Stock per batch with expiry and cost |
| `purchases`          | Batches bought from suppliers |
| `sales`              | Bills with tax, discount and payment mode |
| `sale_items`         | Lines on each bill, tied to a batch |
| `prescriptions`      | Doctor, licence, date and validity |
| `prescription_items` | Medicines on each prescription |

## Security notes

- Passwords are stored as Werkzeug hashes.
- Every form posts with a CSRF token.
- Customers can only open their own prescriptions.
- Session cookies are HTTP-only, SameSite=Lax, and Secure on Vercel.
