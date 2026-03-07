# Mechanic Shop API

Flask + SQLAlchemy backend for a mechanic shop workflow.  
It currently supports customer management, mechanic management, and service-ticket assignment flows.

## Current Capabilities

- Customer CRUD endpoints
- Mechanic create/list/update/delete endpoints
- Service ticket create/list endpoints
- Assign and remove mechanics from a service ticket
- SQLAlchemy models for customers, vehicles, mechanics, service tickets, parts, and join tables

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Marshmallow / Marshmallow
- MySQL (`mysql-connector-python`)

## Project Structure

```text
mechanic_shop_api_db/
|-- app.py
|-- config.py
`-- app/
    |-- __init__.py
    |-- extensions.py
    |-- models.py
    |-- blueprints/
    |   |-- customers/
    |   |   |-- __init__.py
    |   |   `-- routes.py
    |   |-- mechanics/
    |   |   |-- __init__.py
    |   |   |-- routes.py
    |   |   `-- schemas.py
    |   `-- service_tickets/
    |       |-- __init__.py
    |       |-- routes.py
    |       `-- schemas.py
    `-- schemas/
        |-- __init__.py
        |-- customer_schema.py
        |-- mechanic_schema.py
        |-- part_schema.py
        |-- service_ticket_schema.py
        `-- vehicle_schema.py
```

## Setup

1. Create and activate a virtual environment:

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

4. Update `Config.SQLALCHEMY_DATABASE_URI` in `config.py` with your MySQL credentials.

## Run the API

```powershell
python app.py
```

Server default: `http://127.0.0.1:5000`

Note: there is no `/` route right now; start testing at `/customers/`, `/mechanics/`, or `/service-tickets/`.

## Endpoints

### Customers

- `POST /customers/`
- `GET /customers/`
- `GET /customers/<int:customer_id>`
- `PUT /customers/<int:customer_id>`
- `DELETE /customers/<int:customer_id>`

### Mechanics

- `POST /mechanics/`
- `GET /mechanics/`
- `PUT /mechanics/<int:id>`
- `DELETE /mechanics/<int:id>`

### Service Tickets

- `POST /service-tickets/`
- `GET /service-tickets/`
- `PUT /service-tickets/<int:ticket_id>/assign-mechanic/<int:mechanic_id>`
- `PUT /service-tickets/<int:ticket_id>/remove-mechanic/<int:mechanic_id>`

## Quick Request Examples

Create customer:

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

Create service ticket:

```json
{
  "customer_id": 1,
  "vehicle_id": 1,
  "status": "open",
  "odometer_in": 92000,
  "complaint": "Brake noise while stopping"
}
```

Assign mechanic to ticket:

```json
{
  "role": "Lead Technician",
  "hours_worked": 1.5
}
```

## Notes

- `db.create_all()` is called on startup, so tables are auto-created if they do not exist.
- A Postman collection is included: `Mechanic Shop API.postman_collection.json`.
- `config.py` currently stores DB credentials in code; moving this to environment variables is recommended.
