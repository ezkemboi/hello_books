"""
This file contains all application configurations
"""
import os


class Config(object):
    """
    All common configurations for app goes here.
    """
    DEBUG = False
    CSRF_ENABLED = True
    TESTING = False
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class DevelopmentConfig(Config):
    """
    Only development configurations goes here.
    """
    DEBUG = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    """
    Configuration for testing goes here.
    """
    TESTING = True
    DEBUG = True
    SECRET_KEY = "SecretKeyFortesting"
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/hello_book"


class StagingConfig(Config):
    """
    Contains all configurations for staging stage
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    Only production configurations goes here.
    """
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}
