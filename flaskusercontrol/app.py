import logging

from flasgger import Swagger
from flask import Flask, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate
from werkzeug.exceptions import MethodNotAllowed, NotFound

from flaskusercontrol import create_app, db
from flaskusercontrol.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()
swagger = Swagger(app)

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"


class UserSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=80))
    email = fields.String(
        required=True,
        validate=[
            validate.Regexp(EMAIL_REGEX, error="Invalid email format"),
            validate.Length(max=120),
        ],
    )
    password = fields.String(
        required=True, validate=validate.Length(min=6, max=255), load_only=True
    )


class UserUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=80))
    email = fields.String(
        validate=[
            validate.Regexp(EMAIL_REGEX, error="Invalid email format"),
            validate.Length(max=120),
        ]
    )
    password = fields.String(validate=validate.Length(min=6, max=255), load_only=True)


@app.route("/")
def home():
    return jsonify({"message": "Welcome to Flask API!"})


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, NotFound):
        return jsonify({"error": "Not Found"}), 404
    if isinstance(e, MethodNotAllowed):
        return jsonify({"error": "Method Not Allowed"}), 405

    logger.exception("Internal error: %s", e)
    return jsonify({"error": "An internal error occurred"}), 500


@app.route("/users", methods=["POST"])
def create_user():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        validated_data = UserSchema().load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    name = validated_data["name"]
    email = validated_data["email"]
    password = validated_data["password"]

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    try:
        new_user = User(name=name, email=email)
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
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        validated_data = UserUpdateSchema().load(json_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if "name" in validated_data:
            user.name = validated_data["name"]

        if "email" in validated_data:
            new_email = validated_data["email"]
            existing_email = User.query.filter(
                User.email == new_email, User.id != user_id
            ).first()
            if existing_email:
                return jsonify({"error": "Email already exists"}), 400
            user.email = new_email

        if "password" in validated_data:
            user.set_password(validated_data["password"])

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
