import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv(dotenv_path=".flaskenv")

basedir = os.path.abspath(os.path.dirname(__file__))


# for local machine
class Config:

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "sm_app.db")
    SQLALCHEMY_BINDS = {
        # "users": "sqlite:///" + os.path.join(basedir, "sm_app.db"),
        "quran": "sqlite:///"
        + os.path.join(basedir, "quran-metadata.db"),
    }

    JWT_TOKEN_LOCATION = ["headers", "cookies", "json", "query_string"]
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


"""


# for production
class Config:

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "sm_app.db")
    JWT_TOKEN_LOCATION = ["headers", "cookies", "json", "query_string"]
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "secret-key"
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = "None"
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_CSRF_PROTECT = False


"""
