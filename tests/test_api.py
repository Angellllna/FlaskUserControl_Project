import pytest

from flaskusercontrol.app import create_app
from flaskusercontrol.globals import db
from flaskusercontrol.models import User
from tests.test_config import TestConfig


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_user(client):
    payload = {"name": "John Doe", "email": "john@example.com", "password": "secret123"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "User created successfully"


def test_create_user_missing_fields(client):
    payload = {"name": "John Doe", "email": "john@example.com"}
    response = client.post("/users", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_get_users(client):
    payload = {"name": "John Doe", "email": "john@example.com", "password": "secret123"}
    client.post("/users", json=payload)

    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

    assert len(data) >= 1


# command run: pytest tests/test_api.py
