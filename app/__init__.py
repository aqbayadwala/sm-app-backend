from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv(dotenv_path=".flaskenv")

sm_app = Flask(__name__)
sm_app.config.from_object(Config)
db = SQLAlchemy(sm_app)
migrate = Migrate(sm_app, db)
CORS(
    sm_app, origins=["https://daur-material-ui.netlify.app"], supports_credentials=True
)
bcrypt = Bcrypt(sm_app)
jwt = JWTManager(sm_app)

from app import routes
