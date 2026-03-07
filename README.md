# Mechanic Shop API

A Flask + SQLAlchemy API for managing mechanic shop data (customers, vehicles, service tickets, mechanics, and parts).

## Current Status

- App factory and database models are in place.
- Customer CRUD endpoints are implemented.
- Other domains (vehicles, mechanics, parts, service tickets) are modeled and have schemas, but routes are not added yet.

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- Marshmallow / Flask-Marshmallow
- MySQL (`mysql-connector-python`)

## Project Structure

```text
mechanic_shop_api_db/
|- app.py
|- config.py
|- requirements.txt
|- app/
|  |- __init__.py
|  |- extensions.py
|  |- models.py
|  |- blueprints/
|  |  `- customers/
|  |     |- __init__.py
|  |     `- routes.py
|  `- schemas/
|     |- __init__.py
|     |- customer_schema.py
|     |- vehicle_schema.py
|     |- mechanic_schema.py
|     |- part_schema.py
|     `- service_ticket_schema.py
```

## Setup

1. Create and activate a virtual environment (optional if you already use `venv/`):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create the MySQL database:

```sql
CREATE DATABASE mechanic_shop_api_db;
```

4. Set your connection string in `config.py` (`Config.SQLALCHEMY_DATABASE_URI`).

## Run the App

```powershell
python app.py
```

The API will be available at:

- `http://127.0.0.1:5000/`

## API Endpoints (Implemented)

Base path for customer routes: `/customers`

- `POST /customers/` - Create customer
- `GET /customers/` - Get all customers
- `GET /customers/<customer_id>` - Get one customer
- `PUT /customers/<customer_id>` - Update customer
- `DELETE /customers/<customer_id>` - Delete customer

### Example: Create Customer

```http
POST /customers/
Content-Type: application/json
```

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "phone": "555-123-4567",
  "address_line1": "123 Main St",
  "city": "Denver",
  "state": "CO",
  "postal_code": "80202"
}
```

## Notes

- Tables are created automatically on startup via `db.create_all()`.
- The current config uses a direct connection string in `config.py`; consider moving credentials to environment variables before sharing/deploying.
