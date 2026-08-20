# RapidCart

RapidCart is a FastAPI backend for a marketplace-style order management system. It supports JWT authentication, refresh-token rotation, role-based access control, seller product management, buyer order creation, order-status updates, and real-time buyer notifications over WebSockets.

This project was built as a FastAPI learning and technical-test practice project.

## Features

- User registration and login
- Password hashing with bcrypt
- JWT access tokens
- Hashed refresh tokens with rotation and logout support
- Buyer, seller, and admin roles
- Seller-owned product create, read, update, and delete operations
- Buyer order creation with stock validation
- Order totals calculated from product prices at purchase time
- Buyer and seller order listing
- Role-aware order access and status updates
- WebSocket notifications when an order status changes
- Health check endpoint with database connectivity check
- Interactive API documentation through Swagger UI and ReDoc

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- python-jose
- Passlib and bcrypt
- WebSockets
- Uvicorn

## Project Structure

```text
RapidCart/
|-- app/
|   |-- core/        # Settings, security helpers, and auth dependencies
|   |-- db/          # SQLAlchemy engine, session, and base model
|   |-- models/      # Database models
|   |-- routers/     # HTTP and WebSocket routes
|   |-- schemas/     # Pydantic request and response schemas
|   |-- services/    # Business logic and WebSocket connection manager
|   `-- main.py      # FastAPI application entry point
|-- requirements.txt
`-- README.md
```

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd RapidCart
```

If you are already inside the parent folder, move into the project directory:

```bash
cd RapidCart
```

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL Database

Make sure PostgreSQL is running, then create a database:

```sql
CREATE DATABASE rapidcart;
```

### 5. Configure Environment Variables

Create a `.env` file in the `RapidCart` directory:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/rapidcart
SECRET_KEY=replace-this-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

`DATABASE_URL` and `SECRET_KEY` are required. The other values have defaults in `app/core/config.py`.

The application currently creates missing tables on startup with SQLAlchemy's `Base.metadata.create_all`. For production usage, replace this with proper database migrations.

## Run the API

From the `RapidCart` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `GET /health`

The root endpoint is also available at `GET /` and returns a simple test response.

## Authentication

### Register

Endpoint:

```http
POST /auth/register
```

Example request:

```json
{
  "email": "buyer@example.com",
  "password": "secure-password",
  "role": "buyer"
}
```

Valid roles are:

- `buyer`
- `seller`
- `admin`

If no role is provided, the user is registered as a buyer.

### Login

Endpoint:

```http
POST /auth/login
```

This endpoint uses OAuth2 form data. The `username` field should contain the user's email.

```text
username=buyer@example.com
password=secure-password
```

Example response:

```json
{
  "access_token": "<jwt-access-token>",
  "refresh_token": "<refresh-token>",
  "token_type": "bearer"
}
```

Use the access token on protected HTTP routes:

```http
Authorization: Bearer <jwt-access-token>
```

### Refresh Token

Endpoint:

```http
POST /auth/refresh
```

Example request:

```json
{
  "refresh_token": "<refresh-token>"
}
```

The old refresh token is revoked and a new access token plus refresh token are returned.

### Logout

Endpoint:

```http
POST /auth/logout
```

Example request:

```json
{
  "refresh_token": "<refresh-token>"
}
```

Logout revokes the provided refresh token.

## Roles and Permissions

All product and order endpoints require authentication.

| Capability | Buyer | Seller | Admin |
| --- | --- | --- | --- |
| Browse products | Yes | Yes | Yes |
| Create products | No | Yes | No |
| Update products | No | Own products only | No |
| Delete products | No | Own products only | No |
| Create orders | Yes | No | No |
| View order by ID | Own orders | Orders containing their products | Any order |
| List orders | Own orders through `/orders/me` | Relevant orders through `/orders/seller` | No dedicated list route |
| Update order status | Cancel own pending or confirmed orders | Valid transitions for orders containing their products | Any status transition |

Invalid or missing authentication returns `401 Unauthorized`. Authenticated users without permission receive `403 Forbidden`.

## Product API

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/products` | Create a product as a seller |
| `GET` | `/products` | List all products |
| `GET` | `/products/{product_id}` | Get one product |
| `PUT` | `/products/{product_id}` | Update an owned product as a seller |
| `DELETE` | `/products/{product_id}` | Delete an owned product as a seller |

Example product request:

```json
{
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse",
  "price": 799.0,
  "stock": 25
}
```

## Order API

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/orders` | Create an order as a buyer |
| `GET` | `/orders/me` | List the current buyer's orders |
| `GET` | `/orders/seller` | List orders containing the current seller's products |
| `GET` | `/orders/{order_id}` | Get an accessible order |
| `PATCH` | `/orders/{order_id}/status` | Update an order status |

Example order request:

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

When an order is created:

- The order must contain at least one item.
- Each product must exist.
- Requested quantity must be available in stock.
- Product stock is reduced.
- `price_at_purchase` is stored for each order item.
- The order total is calculated automatically.

## Order Status Flow

The normal status flow is:

```text
pending -> confirmed -> processing -> shipped -> delivered
```

Orders can be cancelled from:

```text
pending -> cancelled
confirmed -> cancelled
```

Status update rules:

- Sellers can update orders only when the order contains one of their products.
- Sellers must follow the valid status transition flow.
- Buyers can only cancel their own orders while they are `pending` or `confirmed`.
- Admins can override the normal transition rules.

## WebSocket Notifications

Buyers can connect to the order notification WebSocket with an access token:

```text
ws://127.0.0.1:8000/ws/orders?token=<jwt-access-token>
```

When an order status changes, the connected buyer receives a message like:

```json
{
  "event": "order_status_updated",
  "order_id": 42,
  "status": "shipped"
}
```

The WebSocket accepts client messages as keep-alives, but it does not process them as commands.

If the token is missing or invalid, the server closes the connection with policy violation code `1008`.

## Main Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Basic test endpoint |
| `GET` | `/health` | Database health check |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Login and receive tokens |
| `POST` | `/auth/refresh` | Rotate refresh token |
| `POST` | `/auth/logout` | Revoke refresh token |
| `POST` | `/products` | Create product |
| `GET` | `/products` | List products |
| `GET` | `/products/{product_id}` | Get product |
| `PUT` | `/products/{product_id}` | Update product |
| `DELETE` | `/products/{product_id}` | Delete product |
| `POST` | `/orders` | Create order |
| `GET` | `/orders/me` | List buyer orders |
| `GET` | `/orders/seller` | List seller orders |
| `GET` | `/orders/{order_id}` | Get order |
| `PATCH` | `/orders/{order_id}/status` | Update order status |
| `WS` | `/ws/orders?token=<token>` | Receive order-status notifications |

## Security Notes

- Passwords are hashed before storage.
- Refresh tokens are stored as hashes, not raw token strings.
- Refresh tokens can expire and be revoked.
- Keep `.env` private and do not commit real secrets.
- Use a strong `SECRET_KEY` in every environment.

## Current Notes

- The app uses automatic table creation at startup for development convenience.
- Tests are not included yet.
- Alembic is listed in the dependencies, but migrations are not configured yet.

## License

This project is for learning and technical-test practice.
