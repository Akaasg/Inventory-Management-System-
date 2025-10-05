# Inventory Management System

A Flask web application to manage products, locations, and product movements, with a balance report per location.

## Run

```cmd
cd C:\Users\Akash\Documents\flask
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` in your browser.

## Project Structure

```
flask/
├── app.py               # Main Flask app (routes, DB init, logic)
├── add_test_data.py     # Optional: seed script to add sample data
├── requirements.txt     # Python dependencies
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── add_product.html
│   ├── edit_product.html
│   ├── locations.html
│   ├── add_location.html
│   ├── edit_location.html
│   ├── movements.html
│   ├── add_movement.html
│   ├── edit_movement.html
│   └── balance_report.html
└── static/              # Static assets (optional)
```

## Database

- SQLite database file: `inventory.db` (auto-created on first run)
- Tables: `Product`, `Location`, `ProductMovement`
- Balance report computes per product/location: incoming (to_location) minus outgoing (from_location)

## Notes

- To start fresh, delete `inventory.db` and run `python app.py`.
- To add sample data, run `python add_test_data.py` once.


