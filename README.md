# Rental Backend API

REST API for a rental housing service built with Django REST Framework.

The project supports landlords publishing rental listings and tenants searching, booking and reviewing properties.

## Technologies

- Python 3.13
- Django
- Django REST Framework
- MySQL
- SimpleJWT
- django-filter
- drf-yasg
- Docker
- Docker Compose

## Features

### Authentication

- User registration
- JWT access and refresh tokens
- Logout with refresh token blacklist
- Current user endpoint
- Custom user model
- Tenant and landlord roles

### Listings

Landlords can:

- Create listings
- Update their own listings
- Delete their own listings
- Activate or deactivate listings

Users can:

- View active listings
- Search by title and description
- Filter by city and district
- Filter by minimum and maximum price
- Filter by room count
- Filter by property type
- Order listings by price or creation date

### Bookings

Tenants can:

- Create bookings
- View their bookings
- Cancel bookings before they start

Landlords can:

- View bookings for their listings
- Confirm booking requests
- Reject booking requests

The API prevents:

- Booking inactive listings
- Booking your own listing
- Invalid date ranges
- Booking dates in the past
- Overlapping active bookings

Bookings can be viewed as:

- Active
- Completed

### Reviews

Users can leave a review only if they have completed a confirmed rental.

Reviews support:

- Rating from 1 to 5
- Text comment
- One review per user per listing
- Public review viewing
- Filtering by listing and rating

## API Documentation

Swagger:

```text
http://127.0.0.1:8000/swagger/
```

ReDoc:

```text
http://127.0.0.1:8000/redoc/
```

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
DJANGO_SECRET_KEY=your-secret-key

DB_NAME=rental_db
DB_USER=rental_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

MYSQL_ROOT_PASSWORD=your-root-password
```

Do not commit the real `.env` file to Git.

## Running with Docker

### 1. Create environment file

```bash
cp .env.example .env
```

Set your own values in `.env`.

Docker Compose overrides `DB_HOST` with the MySQL service name `db`.

### 2. Build and start the project

```bash
docker compose up --build
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

### 3. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

### 4. Stop the project

```bash
docker compose down
```

## Running Locally

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the MySQL database and configure `.env`.

Apply migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

## Tests

Run all automated tests locally:

```bash
python manage.py test
```

Run all tests inside Docker:

```bash
docker compose exec web python manage.py test
```

The project currently contains automated API tests for:

- Listings
- Bookings
- Reviews

## Main API Endpoints

### Accounts

```text
POST /api/accounts/register/
GET  /api/accounts/me/
POST /api/accounts/logout/
```

### JWT

```text
POST /api/token/
POST /api/token/refresh/
```

### Listings

```text
GET    /api/listings/
POST   /api/listings/
GET    /api/listings/{id}/
PATCH  /api/listings/{id}/
DELETE /api/listings/{id}/
```

Example filters:

```text
/api/listings/?min_price=500&max_price=1500
/api/listings/?city=Cologne
/api/listings/?min_rooms=2
/api/listings/?property_type=apartment
/api/listings/?search=center
/api/listings/?ordering=price
/api/listings/?ordering=-created_at
```

### Bookings

```text
GET  /api/bookings/
POST /api/bookings/

GET  /api/bookings/{id}/

POST /api/bookings/{id}/confirm/
POST /api/bookings/{id}/reject/
POST /api/bookings/{id}/cancel/

GET /api/bookings/active/
GET /api/bookings/completed/
```

### Reviews

```text
GET    /api/reviews/
POST   /api/reviews/
GET    /api/reviews/{id}/
PATCH  /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

Example filters:

```text
/api/reviews/?listing=1
/api/reviews/?rating=5
```

## Project Structure

```text
rental_backend/
├── accounts/
├── bookings/
├── listings/
├── reviews/
├── config/
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Roles

### Tenant

Can:

- View listings
- Search and filter listings
- Create bookings
- Cancel own bookings
- Leave reviews after completed rentals

### Landlord

Can:

- View listings
- Create listings
- Edit own listings
- Delete own listings
- View booking requests for own listings
- Confirm or reject bookings

## Test Database Setup

On first startup with a fresh MySQL data volume, Docker automatically executes `mysql-init/01-grant-test-db.sh`.

This script grants the application user the necessary permissions to create and manage the separate test database.

To start the application:

```bash
docker compose up --build -d
```

To run the automated tests:

```bash
docker compose exec web python manage.py test
```

The initialization script runs only when the MySQL data volume is created for the first time. Existing databases are not modified automatically.
