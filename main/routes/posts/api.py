from flask import request
from werkzeug.exceptions import NotFound

from extensions import db
from main import posts_bp
from main.models import User, Posts
from services.user_service import UserService

user_service = UserService()


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
