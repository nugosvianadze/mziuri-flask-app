import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    DB_PATH = os.path.join(BASE_DIR, "instance", "mziuri.db")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"