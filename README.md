# Mechanic Shop API

Flask + SQLAlchemy backend for a mechanic shop workflow. It manages customers,
vehicles, mechanics, service tickets, and parts inventory, with JWT
authentication, rate limiting, response caching, and advanced queries.

## Features

- **Customer, Vehicle, Mechanic, Service Ticket, and Inventory** resources with full CRUD
- **JWT token authentication** (python-jose) for both customers and mechanics
  - Customer login issues a customer-scoped token; mechanic login issues a mechanic-scoped token (distinguished by a `role` claim)
  - `@token_required` and `@mechanic_token_required` decorators protect routes and pass the authenticated id to the handler
- **Rate limiting** (Flask-Limiter) with a blanket default of 200/hour plus tighter caps on write/auth routes
- **Response caching** (Flask-Caching) on the customer list endpoint, query-string aware so each page caches separately
- **Advanced queries**
  - Bulk add/remove mechanics on a ticket in one request
  - Mechanics ranked by number of tickets worked
  - Pagination on the customer list
- **Inventory**: parts catalog linked to tickets through a `quantity`-bearing junction table

## Tech Stack

- Python / Flask
- Flask-SQLAlchemy
- Flask-Marshmallow / Marshmallow
- Flask-Limiter (rate limiting)
- Flask-Caching (caching)
- python-jose (JWT)
- MySQL (`mysql-connector-python`)

## Project Structure

```text
mechanic_shop_api_db/
|-- app.py
|-- config.py                     # DB URI + SECRET_KEY (JWT signing)
|-- requirements.txt
|-- Mechanic Shop API.postman_collection.json
`-- app/
    |-- __init__.py               # app factory; registers all blueprints
    |-- auth.py                   # encode_token, encode_mechanic_token, decorators
    |-- extensions.py             # db, ma, limiter, cache
    |-- models.py                 # all SQLAlchemy models + junction tables
    `-- blueprints/
        |-- customers/            # /login, /my-tickets, paginated CRUD
        |-- mechanics/            # /login, /top, CRUD
        |-- service_tickets/      # CRUD, /<id>/edit, /<id>/add-part, assign/remove
        |-- inventory/            # CRUD (writes require a mechanic token)
        `-- vehicles/             # CRUD
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

4. Update `Config.SQLALCHEMY_DATABASE_URI` in `config.py` with your MySQL
   credentials. Set `SECRET_KEY` (env var `SECRET_KEY`) for JWT signing; a dev
   fallback is used if unset.

## Run the API

```powershell
python app.py
```

Server default: `http://127.0.0.1:5000`

There is no `/` route; start at `/customers/`, `/mechanics/`,
`/service-tickets/`, or `/inventory/`. `db.create_all()` runs on startup, so
new tables are created automatically.

## Authentication

1. Create a customer (or mechanic) with a `password` field.
2. `POST /customers/login` (or `/mechanics/login`) with `email` + `password`.
3. The response returns a `token`. Send it on protected routes as a header:

```text
Authorization: Bearer <token>
```

Customer tokens unlock customer routes; mechanic tokens unlock mechanic/inventory
routes. Using the wrong token type returns `403`.

## Endpoints

### Auth

- `POST /customers/login` — returns a customer JWT
- `POST /mechanics/login` — returns a mechanic JWT

### Customers

- `POST /customers/` — create (rate limited 5/min; accepts `password`)
- `GET /customers/?page=<n>&per_page=<n>` — paginated list (cached 60s)
- `GET /customers/<int:customer_id>`
- `GET /customers/my-tickets` — **customer token**; tickets for the logged-in customer
- `PUT /customers/` — **customer token**; updates the authenticated customer
- `DELETE /customers/` — **customer token**; deletes the authenticated customer

### Mechanics

- `POST /mechanics/` — create (accepts `password`)
- `GET /mechanics/`
- `GET /mechanics/top` — mechanics ranked by tickets worked (busiest first)
- `GET /mechanics/<int:id>`
- `PUT /mechanics/<int:id>`
- `DELETE /mechanics/<int:id>`

### Service Tickets

- `POST /service-tickets/`
- `GET /service-tickets/`
- `GET /service-tickets/<int:ticket_id>`
- `PUT /service-tickets/<int:ticket_id>`
- `DELETE /service-tickets/<int:ticket_id>`
- `PUT /service-tickets/<int:ticket_id>/edit` — **mechanic token**; bulk add/remove mechanics via `add_ids` / `remove_ids`
- `POST /service-tickets/<int:ticket_id>/add-part` — **mechanic token**; attach an inventory part with a quantity
- `PUT /service-tickets/<int:ticket_id>/assign-mechanic/<int:mechanic_id>`
- `PUT /service-tickets/<int:ticket_id>/remove-mechanic/<int:mechanic_id>`

### Inventory

- `POST /inventory/` — **mechanic token**
- `GET /inventory/`
- `GET /inventory/<int:inventory_id>`
- `PUT /inventory/<int:inventory_id>` — **mechanic token**
- `DELETE /inventory/<int:inventory_id>` — **mechanic token**

## Quick Request Examples

Create customer (include a password to enable login):

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "password": "secret123",
  "phone": "555-123-4567",
  "city": "Denver",
  "state": "CO",
  "postal_code": "80202"
}
```

Login:

```json
{
  "email": "jane@example.com",
  "password": "secret123"
}
```

Bulk edit a ticket's mechanics:

```json
{
  "add_ids": [1, 2],
  "remove_ids": [3]
}
```

Add a part to a ticket:

```json
{
  "inventory_id": 1,
  "quantity": 2
}
```

## Notes

- A Postman collection is included: `Mechanic Shop API.postman_collection.json`.
  Run the **Auth** folder first — the login requests auto-save tokens into the
  `{{customer_token}}` and `{{mechanic_token}}` collection variables used by
  protected requests.
- `config.py` stores DB credentials in code; moving them to environment
  variables is recommended.
