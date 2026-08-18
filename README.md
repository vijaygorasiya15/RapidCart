# RapidCart

RapidCart is a learning project for building a **Real-Time Order Management System** with FastAPI. The aim is to deliver a clean, functional backend within a two-day technical-test timeframe while keeping the implementation understandable and practical.

> **Project status:** Initial setup — features will be implemented incrementally.

## Project Goals

- Build REST APIs with FastAPI.
- Use PostgreSQL and SQLAlchemy for persistent data.
- Implement JWT-based authentication and role-based access control (RBAC).
- Support three user roles: **Buyer**, **Seller**, and **Admin**.
- Manage products, orders, order items, and order-status updates.
- Notify relevant buyers of order-status changes in real time through WebSockets.
- Add tests for the main API flows and permissions.

## Planned Features

### Authentication and RBAC

- User registration and login
- Secure password hashing
- JWT access tokens
- Reusable current-user and role-check dependencies
- Buyer, Seller, and Admin permissions

### Products and Orders

- Seller product management
- Product browsing for buyers
- Order creation and order details
- Buyer order tracking
- Seller order access and status updates
- Admin management endpoints

### Order Lifecycle

```text
PENDING → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
    └────────────────────────────→ CANCELLED
```

Status changes will be validated and restricted according to the user role.

### Real-Time Updates

When a seller or admin updates an order status, the relevant connected buyer will receive a WebSocket notification.

## Planned Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT authentication
- WebSockets
- Pytest / FastAPI testing tools

## Intended Project Structure

```text
app/
├── main.py
├── core/          # Configuration, security, and dependencies
├── db/            # Database setup and models
├── schemas/       # Pydantic request/response schemas
├── routers/       # API endpoints
├── services/      # Business logic and WebSocket handling
└── tests/         # Automated tests
```

## Development Priorities

This project follows the principle:

```text
Correctness > Simplicity > Completeness > Polish > Advanced Architecture
```

The first implementation focus is the FastAPI/database foundation, authentication, RBAC, and product management. Orders, real-time updates, tests, and final documentation follow afterward.

## API Documentation

Once the FastAPI application is running, interactive API documentation will be available at:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Security Notes

- Passwords will never be stored as plain text.
- JWT secrets and database credentials will be stored in a local `.env` file.
- The `.env` file must not be committed to Git.

## License

This project is for learning and technical-test practice.
