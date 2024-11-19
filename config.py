import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "sm_app.db")
    JWT_TOKEN_LOCATION = ["headers", "cookies", "json", "query_string"]
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "secret-key"
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = "None"
    JWT_COOKIE_HTTPONLY = True
