import time

from flask import session, redirect, url_for, request, render_template
from sqlalchemy import func
from werkzeug.exceptions import NotFound

from extensions import db
from main import posts_bp
from main.models import User, Posts
from main.utils.decorators import login_required


@posts_bp.route("/template", methods=["POST", "GET"])
@login_required
def create_template_post():
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("posts/create_post.html")
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
        post = (
            Posts(
                title=title,
            ))
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
@login_required
def my_posts():
    user_id = session["user_id"]
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
    return render_template("/user/my_posts.html", my_posts=posts_list, status_counts=counts_data)


@posts_bp.route("/<int:post_id>")
@login_required
def post_detail_page(post_id: int):
    post = db.session.get(Posts, post_id)
    if not post:
        return redirect(url_for("posts.my_posts"))
    post.views_count += 1
    db.session.commit()
    return render_template("posts/post_detail.html", post=post)

