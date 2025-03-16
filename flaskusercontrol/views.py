import logging
import re

from flask import Blueprint, Flask, jsonify, request
from werkzeug.exceptions import (
    BadRequest,
    MethodNotAllowed,
    NotFound,
    UnprocessableEntity,
)

from flaskusercontrol.globals import db
from flaskusercontrol.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


users_bp = Blueprint("users", __name__)


EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"


@users_bp.route("/")
def home():
    """
    Home endpoint
    ---
    tags:
      - home
    responses:
      200:
        description: Welcome message
        schema:
          type: object
          properties:
            message:
              type: string
    """
    return jsonify({"message": "Welcome to Flask API!"})


@users_bp.errorhandler(Exception)
def handle_exception(e):
    """
    Handle all exceptions
    """
    if isinstance(e, NotFound):
        return jsonify({"error": "Not Found"}), 404
    if isinstance(e, MethodNotAllowed):
        return jsonify({"error": "Method Not Allowed"}), 405
    if isinstance(e, BadRequest):
        return jsonify({"error": "Bad Request"}), 400
    if isinstance(e, UnprocessableEntity):
        return jsonify({"error": "Unprocessable Entity"}), 422

    logger.exception("Internal error: %s", e)
    return jsonify({"error": "An internal error occurred"}), 500


@users_bp.route("/users", methods=["POST"])
def create_user():
    """
    Create a new user
    ---
    tags:
      - users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: User
          required:
            - name
            - email
            - password

          properties:
            name:
              type: string
              example: John Doe
            email:
              type: string
              example: john_doe@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: An error occurred during user creation
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields: name, email, password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    try:
        new_user = User(name=name, email=email)

        if password:
            new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        logger.info("User %s created successfully", email)
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logger.exception("Error during user creation for email %s: %s", email, e)
        return jsonify({"error": "An error occurred during user creation"}), 500


@users_bp.route("/users", methods=["GET"])
def get_users():
    """
    Get all users
    ---
    tags:
      - users
    responses:
      200:
        description: List of users
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              email:
                type: string
              created_at:
                type: string
      500:
        description: An error occurred getting users
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        users = User.query.all()
        users_list = [user.to_dict() for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        logger.exception("Error getting users: %s", e)
        return jsonify({"error": "An error occurred getting users"}), 500


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    """
    Get user by id
    ---
    tags:
      - users
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
            created_at:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: An error occurred getting user
        schema:
          type: object
          properties:
            error:
              type: string
    """

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        logger.exception("Error getting user by id %s: %s", user_id, e)
        return jsonify({"error": "An error occurred getting user"}), 500


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Update user details
    ---
    tags:
      - users
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          id: User
          properties:
            name:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: User updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: An error occurred updating user
        schema:
          type: object
          properties:
            error:
              type: string
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        new_name = data.get("name")
        if new_name:
            user.name = new_name

        new_email = data.get("email")
        if new_email:
            existing_email = User.query.filter(
                User.email == new_email, User.id != user_id
            ).first()
            if existing_email:
                return jsonify({"error": "Email already exists"}), 400
            user.email = new_email

        new_password = data.get("password")
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        logger.info("User %s updated successfully", user.email)
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.exception("Error updating user with id %s: %s", user_id, e)
        return jsonify({"error": "An error occurred updating user"}), 500


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete user by id
    ---
    tags:
      - users
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
    responses:
      200:
        description: User deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: An error occurred deleting user
        schema:
          type: object
          properties:
            error:
              type: string
    """

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.exception("Error deleting user: %s", e)
        return jsonify({"error": "An error occurred while deleting user"}), 500
