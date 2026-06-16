from datetime import datetime, timezone, timedelta

from flask import Blueprint, render_template, redirect, url_for, session
from sqlalchemy import func
from flask_security import login_user, login_required, logout_user

from main.models import Posts
from main.models.user import User
from extensions import db
from services.user_service import UserService

main_bp = Blueprint("home", __name__, url_prefix="/")
user_service = UserService()

@main_bp.route("/home", methods=["GET"])
@main_bp.route("/")
@login_required
def home():
    now = datetime.now(tz=timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    print(one_hour_ago)
    users = db.session.scalars(db.select(User).limit(10)).all()
    latest_posts_count = db.session.scalar(db.select(func.count(Posts.id)).
                              where(Posts.created_at >= one_hour_ago))
    last_four_posts = db.session.execute(db.select(Posts).
                                         where(Posts.status == "published").
                                         order_by(Posts.created_at.desc()).limit(4)).scalars()

    return render_template("main/index.html", users=users,
                           latest_posts=latest_posts_count,
                           last_four_posts=last_four_posts)