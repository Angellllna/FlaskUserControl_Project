from flasgger import Swagger
from flask import Flask

from flaskusercontrol.config import Config
from flaskusercontrol.globals import bcrypt, db, jwt, migrate
from flaskusercontrol.models import User
from flaskusercontrol.views import users_bp


def create_app(custom_config=None):
    app = Flask(__name__)
    app.config.from_object(custom_config or Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    migrate.init_app(app, db)
    app.register_blueprint(users_bp)
    swagger = Swagger(app)

    return app


if __name__ == "__main__":
    create_app().run(debug=True, host="0.0.0.0", port=5001)
