# Priscah Retail Hardware System

A Flask-based retail hardware point-of-sale and inventory system for plumbing, electrical, and general construction departments.

## Login Accounts

- Administrator: `admin` / `Admin@2026`
- Cashier: `cashier` / `Cashier@2026`

## Features

- Multi-department cart sales
- Cashier checkout
- M-Pesa/card/cash payment recording
- Stock management
- Returns processing
- Department sales reports
- CSV export
- Audit logs
- Full-screen login background image

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: `http://127.0.0.1:5051`

## Render Deployment

Render can deploy this repo using `render.yaml`.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
