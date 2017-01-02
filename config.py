import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('FLASK_BY_EXAMPLE_KEY')


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = os.environ.get('FLASK_BY_EXAMPLE_KEY')


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = os.environ.get('FLASK_BY_EXAMPLE_KEY')


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = os.environ.get('FLASK_BY_EXAMPLE_KEY')
