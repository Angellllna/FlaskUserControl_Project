import logging
import re

from flask import jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.exceptions import MethodNotAllowed, NotFound
from flaskusercontrol import create_app, db
from flaskusercontrol.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = create_app()

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"


@app.route("/")
def home():
    return jsonify({"message": "Welcome to Flask API!"})


@app.errorhandler(Exception)
def handle_exception(e):
    """
    Глобальний обробник помилок: логуємо та повертаємо 500, якщо це не 404/405.
    """
    if isinstance(e, NotFound):
        return jsonify({"error": "Not Found"}), 404
    if isinstance(e, MethodNotAllowed):
        return jsonify({"error": "Method Not Allowed"}), 405

    logger.exception("Internal error: %s", e)
    return jsonify({"error": "An internal error occurred"}), 500


@app.route("/users", methods=["POST"])
def create_user():
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


@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = User.query.all()
        users_list = [user.to_dict() for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        logger.exception("Error getting users: %s", e)
        return jsonify({"error": "An error occurred getting users"}), 500


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        logger.exception("Error getting user by id %s: %s", user_id, e)
        return jsonify({"error": "An error occurred getting user"}), 500


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
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


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
