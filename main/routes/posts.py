from flask import Blueprint, request, session, url_for, render_template
from sqlalchemy import func
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect

from main.models.post import Posts
from main.models.user import User
from extensions import db
from services.user_service import UserService

posts_bp = Blueprint("posts", __name__, url_prefix="/api/posts")
user_service = UserService()


@posts_bp.route("/<int:user_id>", methods=["POST"])
def create_post(user_id: int):
    data = request.json
    title = data.get("title")

    if not title.strip():
        return {
            "success": False,
            "message": "title field is required!"
        }, 404

    try:
        user = db.get_or_404(User, user_id)
    except NotFound as e:
        return {
            "success": False,
            "message": f"User with id={user_id}, not found!"
        }, 404

    try:
        # version 1
        # post = Posts(
        #     title=title,
        #     user_id=user_id
        # )
        # db.session.add(post)
        # db.session.commit()

        # version 2
        post = Posts(
            title=title,
        )
        user.posts.append(post)
        db.session.commit()
        return {
            "success": True,
            "message": "post successfully created!",
            "data": post.to_dict()
        }
    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "message": "Try again later!"
        }, 404


@posts_bp.route("/template", methods=["POST", "GET"])
def create_template_post():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("users.login"))

    if request.method == "GET":
        return render_template("create_post.html")
    data = request.form
    title = data.get("title")

    if not title.strip():
        return {
            "success": False,
            "message": "title field is required!"
        }, 404

    try:
        user = db.get_or_404(User, user_id)
    except NotFound as e:
        return {
            "success": False,
            "message": f"User with id={user_id}, not found!"
        }, 404

    try:
        # version 2
        post = Posts(
            title=title,
        )
        user.posts.append(post)
        db.session.commit()
        return redirect(url_for("posts.my_posts"))
    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "message": "Try again later!"
        }, 404

@posts_bp.route("/my-posts")
def my_posts():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("users.login"))
    # 1. Get the quick status summary counts (Returns 2 rows max)
    counts_data = db.session.execute(
        db.select(Posts.status, func.count(Posts.id))
        .where(Posts.user_id == user_id)
        .group_by(Posts.status)
    ).all()
    counts_data = {status: count for status, count in counts_data}
    print(counts_data)
    # 2. Get the actual list of posts (Returns all rows)
    posts_list = db.session.scalars(
        db.select(Posts)
        .where(Posts.user_id == user_id)
    ).all()
    return render_template("my_posts.html", my_posts=posts_list, status_counts=counts_data)

@posts_bp.route("/<int:user_id>")
def get_user_posts(user_id: int) -> tuple[dict, int]:
    try:
        u_data = user_service.get_user_with_id(db, User, user_id)
        user_posts = u_data["user"].to_dict_with_posts()
        return {
            "success": True,
            "data": user_posts
        }, 200
    except Exception as e:
        return {
            "success": False,
            "message": e.message
        }, 500
