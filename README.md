# FlaskUserControl_Project

FlaskUserControl_Project is a REST API for user management built with Flask.  
The API supports basic CRUD operations (Create, Read, Update, Delete) for users and uses SQLAlchemy for database management.

## Features:
- Create a new user (`POST /users`)
- Retrieve a list of all users (`GET /users`)
- Get details of a specific user (`GET /users/{id}`)
- Update user information (`PUT /users/{id}`)
- Delete a user (`DELETE /users/{id}`)

The API is documented using Swagger (Flasgger).  
Containerization is implemented with Docker.
