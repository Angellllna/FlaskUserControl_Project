from flask import Flask

from flaskusercontrol.config import Config
from flaskusercontrol.globals import bcrypt, db, jwt, migrate
from flaskusercontrol.models import User
from flaskusercontrol.views import users_bp
