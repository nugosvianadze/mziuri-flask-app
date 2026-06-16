import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    DB_PATH = os.path.join(BASE_DIR, "instance", "mziuri.db")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SECURITY_PASSWORD_SALT = '146585145368132386173505678016728509634'
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_DEFAULT_REMEMBER_ME = True