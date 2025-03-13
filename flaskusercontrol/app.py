from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route('/')
def home():
    return "FlaskUserControl API is running!"

if __name__ == '__main__':
    app.run(debug=True)
