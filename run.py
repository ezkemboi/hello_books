"""
The file that runs the application
"""
import os
from app import create_app

config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
