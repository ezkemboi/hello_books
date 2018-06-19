"""
This module initializes the application
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from config import app_config

app = Flask(__name__)
api = Api(app, prefix='/api/v1')
app.config.from_object(app_config['production'])
app.url_map.strict_slashes = False
config_name = os.getenv('APP_SETTINGS')
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET')
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
