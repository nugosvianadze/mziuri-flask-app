from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()
# Initialize LoginManager
login_manager = LoginManager()

# Redirect unauthenticated users to the 'login' route
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'