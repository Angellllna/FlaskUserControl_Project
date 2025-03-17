# User Management REST API

This project is a simple REST API for user management built using Flask. It supports CRUD operations (Create, Read, Update, Delete) for managing users and is designed to be containerized with Docker. The project uses `poetry` for dependency management and includes automatic API documentation with Swagger.

## Features

- **Create a new user** (`POST /users`)
- **Retrieve all users** (`GET /users`)
- **Retrieve a specific user by ID** (`GET /users/{id}`)
- **Update user details** (`PUT /users/{id}`)
- **Delete a user** (`DELETE /users/{id}`)
- **Database support** using PostgreSQL via SQLAlchemy
- **Secure password hashing** with bcrypt
- **API documentation** via Flasgger (Swagger)
- **Containerized deployment** with Docker

## Technologies Used

- **Flask** – Web framework
- **SQLAlchemy** – ORM for database interactions
- **Flask-Migrate** – Database migration handling
- **Flask-Bcrypt** – Password hashing
- **Flask-JWT-Extended** – JWT authentication (can be extended later)
- **Flasgger** – Auto-generated API documentation
- **Docker & Docker Compose** – Containerization
- **Poetry** – Dependency management

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/)
- [Docker & Docker Compose](https://www.docker.com/)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

### 2. Install Dependencies

This project uses `poetry` for dependency management. Install dependencies with:

```bash
poetry install
```

### 3. Setup Environment Variables

Create a `.env` file in the root directory and add the following configurations:

```env
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
DATABASE_URL=postgresql://user:password@db:5432/flaskdb
```

### 4. Apply Database Migrations

Run the following command to initialize the database:

```bash
poetry run flask db upgrade
```

## Running the Application

### Locally

Run the Flask application using:

```bash
poetry run python app.py
```

The API will be available at [http://localhost:5001](http://localhost:5001).

### Using Docker

To start the application with Docker, run:

```bash
docker-compose up --build
```

This will start both the Flask application and the PostgreSQL database.

## API Documentation

### Swagger (Flasgger)

This project integrates **Flasgger** to automatically generate API documentation. After starting the application, you can access the Swagger UI at:

[http://localhost:5001/apidocs/](http://localhost:5001/apidocs/)

This interactive interface allows you to test API endpoints directly from your browser by sending requests and viewing responses.

## Running Tests

This project includes basic tests using `pytest`. To run the tests:

```bash
poetry run pytest
```

## Project Structure

```
/
├── flaskusercontrol/
│   ├── __init__.py        # App initialization
│   ├── app.py             # Application entry point
│   ├── config.py          # Configuration settings
│   ├── globals.py         # Global extensions (DB, bcrypt, JWT, etc.)
│   ├── models.py          # User model
│   ├── views.py           # API endpoints
│
├── tests/
│   ├── test_api.py        # API tests
│   ├── test_config.py     # Test configurations
│
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── .env                   # Environment variables
├── README.md              # Project documentation
```

## Future Enhancements

- Implement authentication and authorization
- Extend user model with additional attributes
- Add logging and monitoring features
- Set up CI/CD pipeline for automatic deployment

---
