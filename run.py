"""
The file that runs the application
"""
import os
from app import app
from app.endpoints import api

config_name = os.getenv('APP_SETTINGS')

if __name__ == '__main__':
    app.run()
