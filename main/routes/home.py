from flask import Blueprint, render_template, redirect, url_for, session

from main.models.user import User
from extensions import db
from services.user_service import UserService

main_bp = Blueprint("home", __name__, url_prefix="/api/user_data")
user_service = UserService()

@main_bp.route("/home", methods=["GET"])
@main_bp.route("/")
def home():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    users = db.session.scalars(db.select(User).limit(10)).all()
    return render_template("index.html", users=users)