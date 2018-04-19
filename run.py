"""
The file that runs the application
"""
import os
from app.app import app

config_name = os.getenv('APP_SETTINGS')

if __name__ == '__main__':
    app.run()
