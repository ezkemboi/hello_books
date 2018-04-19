"""
This module initializes the application
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from config import app_config

app = Flask(__name__)
api = Api(app, prefix='/api/v1')
app.config.from_object(app_config['development'])
app.url_map.strict_slashes = False
db = SQLAlchemy(app)
