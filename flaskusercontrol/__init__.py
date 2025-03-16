from flask import Flask

from flaskusercontrol.config import Config
from flaskusercontrol.globals import bcrypt, db, jwt, migrate
from flaskusercontrol.models import User 


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Ініціалізуємо Flask-Migrate
    migrate.init_app(app, db)

    return app
