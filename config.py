import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_PATH = "instance/mziuri.db"
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"