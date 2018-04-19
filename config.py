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


class TestingConfig(Config):
    """
    Configuration for testing goes here.
    """
    TESTING = True
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
    'production': ProductionConfig
}
