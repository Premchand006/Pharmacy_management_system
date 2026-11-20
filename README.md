# Pharmacy Management System

[![CI](https://github.com/Premchand006/Pharmacy_management_system/actions/workflows/ci.yml/badge.svg)](https://github.com/Premchand006/Pharmacy_management_system/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A web app for running a retail chemist's counter in India: GST billing,
batch-wise stock with expiry control, supplier purchases, the drug
registers the Drugs Rules ask for, monthly GST figures, and a portal where
customers can see their prescriptions and bills.

Built with Flask 3 and SQLAlchemy. It runs on SQLite for local use and on
Postgres in production, and deploys to Vercel without extra configuration.

## What it does

### Billing counter

- Search by brand, generic name or barcode (a USB scanner works as a keyboard).
- Stock is taken from the batch that expires first; expired batches are never sold.
- Prices are MRP-inclusive. Taxable value and CGST/SGST are worked out per line and stored on the invoice.
- Invoice numbers run `PREFIX/2026-27/00001` and restart each financial year.
- Schedule H, H1, X and NDPS drugs require patient and prescriber details and a registered pharmacist before the bill can be saved. Schedule X also needs a Form 20F licence on file.
- A portal prescription can be billed directly; the number of repeats the doctor allowed is enforced.
- Prints on A5 or 80 mm thermal paper. Invoices are voided, never deleted, and voiding puts the stock back.

### Stock

- Goods receipt against a supplier invoice; each line becomes a batch with its own MRP and expiry.
- Purchases are refused from suppliers with no drug licence on file or an expired one.
- Batch list filtered by expiring or expired, with stock removal (expiry, damage, return) recorded in the audit log.
- Reorder list from per-product reorder levels.

### Records and reports

- Prescription register for H, H1, X and NDPS supplies; Schedule X register per drug with running balance; purchase register. All export to CSV and print.
- GST figures for a month: B2C by rate, HSN summary, B2B invoices and documents issued, as CSV in the GSTR-1 column layout.
- Batch trace for recalls: supplier, every bill and every prescription a batch went out on.
- Append-only audit log of every create, update, void, stock adjustment and sign-in.

### Customer portal

- Customers sign in with their customer ID and a password set at the counter.
- They see only their own prescriptions and bills, and can send a new prescription ahead of a visit.
- Staff can erase a customer's profile on request. Invoices and registers keep the details copied at the time of sale, because the law requires those records.

## Security

- Passwords hashed with scrypt (N=2^17), upgraded automatically from weaker hashes at sign-in; 12-character minimum.
- Sign-in throttled: 5 failures per account or 20 per IP in 15 minutes locks further attempts. Counts are kept in the database, so this works on serverless.
- Sessions expire after 60 minutes idle. Changing a password or deactivating a user signs out every session.
- CSRF tokens on every form; sign-out is a POST.
- Strict Content-Security-Policy with no inline scripts, Subresource Integrity on CDN files, `no-store` caching on every page, HSTS on Vercel.
- Customer queries are always scoped to the signed-in customer.
- `pip-audit` runs in CI.

## Run locally

Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py
```

Open <http://localhost:5000>. The first start creates `instance/pharmacy.db`
with demo data. `python seed_data.py` wipes it and loads the demo data again.

| Who                    | Sign in at       | Login                   | Password             |
|------------------------|------------------|-------------------------|----------------------|
| Owner (admin)          | `/login`         | `admin`                 | `admin-demo-2026`    |
| Pharmacist             | `/login`         | `meera`                 | `staff-demo-2026`    |
| Counter assistant      | `/login`         | `ravi`                  | `staff-demo-2026`    |
| Customer               | `/portal/login`  | customer ID `1` to `8`  | `customer-demo-2026` |

Run the tests with `pytest`.

## Configuration

| Variable               | Needed            | Purpose |
|------------------------|-------------------|---------|
| `SECRET_KEY`           | Yes, in production | Signs sessions and CSRF tokens. `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL`         | Yes, in production | Postgres URL, e.g. from Neon. `postgres://` is accepted. |
| `SECRET_KEY_FALLBACKS` | No                | Comma-separated old keys, so sessions survive a key rotation. |
| `SESSION_MINUTES`      | No                | Idle sign-out time. Default 60. |
| `TRUSTED_HOSTS`        | No                | Comma-separated host names the app answers to. |
| `SEED_DEMO_DATA`       | No                | `1` loads demo data into an empty database. On by default only for SQLite. |

## Deploy to Vercel

`app.py` exposes `app`, which Vercel picks up as a Flask app. CSS and JS
are in `public/static/` and served from Vercel's CDN. `vercel.json` pins the
function to Singapore (`sin1`), the closest region to India that most
Postgres hosts also offer.

1. Create a Postgres database in Singapore (Neon's `aws-ap-southeast-1` works on its free plan).
2. Import the repository in Vercel and set `SECRET_KEY` and `DATABASE_URL`.
3. Deploy, then sign in and fill in **Settings**: pharmacy name, address, GSTIN and drug licence numbers. They are printed on every invoice.
4. Create staff logins under **Staff**. Remove or change the demo accounts if you loaded demo data.

`/healthz` checks the app and database.

Vercel's free Hobby plan is for non-commercial use. A pharmacy using this
for its business needs the Pro plan or another host. Free Postgres plans
have no real backups; schedule `pg_dump` exports.

The schema is created with `create_all()`. Changing a model on a database
that already holds data needs a migration (for example with Alembic),
which this project does not include yet.

## Layout

```text
app.py                  Entry point (Vercel, flask run, python app.py)
pharmacy/
  __init__.py           App factory, security headers, error pages
  config.py             Settings from environment variables
  models.py             Tables
  billing.py            Batch allocation, GST, invoice numbers, voids
  auth.py               Sign-in, throttling, sessions, role checks
  audit.py              Audit log written on every database flush
  seed.py               Demo data
  views/                Staff, stock, sales, reports and portal pages
  templates/
public/static/          CSS and JS
tests/                  pytest suite
```

## Not legal advice

The register and invoice formats follow the Drugs Rules, 1945 (Rule 65),
the CGST Rules (Rule 46) and the GSTR-1 tables as of 2026, but a
pharmacist and an accountant should check them for your state before you
rely on them.

## License

MIT. See [LICENSE](LICENSE).
