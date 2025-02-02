# project/server/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))
print(f"basedir: {basedir}")


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = os.getenv("APP_NAME", "chore_tracker")
    BCRYPT_LOG_ROUNDS = 4
    DEBUG_TB_ENABLED = False
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = True


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///{0}".format(os.path.join(basedir, "data", "chores_db.sqlite3"))
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""

    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL", "sqlite:///")
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration."""

    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "PROD_DATABASE_URL",
        "sqlite:///{0}".format(os.path.join(basedir, "data", "prod_chores_db.sqlite3")),
    )
    WTF_CSRF_ENABLED = True
