import os
from datetime import timedelta

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem" 
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7) 


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)


from dashboard import views
from dashboard.models import *
from dashboard.models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'dashboard_login'
login_manager.login_message = "Please log in to access this page."
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user
