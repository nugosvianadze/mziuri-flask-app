import time

from flask import session, redirect, url_for, request, render_template, flash
from sqlalchemy import func
from werkzeug.exceptions import NotFound

from extensions import db
from main import posts_bp
from main.models import User, Posts
from flask_login import login_required, current_user

CATEGORY_OPTIONS = ["Daily notes", "Process log", "Studio update", "Field journal"]


@posts_bp.route("/template", methods=["POST", "GET"])
@login_required
def create_template_post():

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
        # version 2
        post = (
            Posts(
                title=title,
            ))
        current_user.posts.append(post)
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
    # 1. Get the quick status summary counts (Returns 2 rows max)
    counts_data = db.session.execute(
        db.select(Posts.status, func.count(Posts.id))
        .where(Posts.user_id == session["_user_id"])
        .group_by(Posts.status)
    ).all()
    counts_data = {status: count for status, count in counts_data}
    print(counts_data)
    # 2. Get the actual list of posts (Returns all rows)
    posts_list = db.session.scalars(
        db.select(Posts)
        .where(Posts.user_id == session["_user_id"])
    ).all()
    return render_template("/user/my_posts.html", my_posts=posts_list, status_counts=counts_data)


@posts_bp.route("/<int:post_id>")
@login_required
def post_detail_page(post_id: int):
    post = db.session.get(Posts, post_id)
    if not post:
        return redirect(url_for("posts.my_posts"))


    if post.status == "draft":
        if session["_user_id"] != post.user_id:
            # user not allowed
            return redirect(url_for("home.home"))

    post.views_count += 1
    db.session.commit()
    return render_template("posts/post_detail.html", post=post)


@posts_bp.route("/update/<int:post_id>", methods=["GET", "POST"])
@login_required
def update(post_id: int):
    post = db.session.get(Posts, post_id)
    if not post:
        return redirect(url_for("posts.my_posts"))

    if request.method == "GET":
        return render_template("posts/edit_post.html", post=post, cat_options=CATEGORY_OPTIONS)

    title, category, description = (request.form.get("title"),
                                    request.form.get("category"),
                                    request.form.get("description"))
    print(f"category - {category}")
    if not title:
        flash('Invalid title value. Please try again.', 'danger')
        return render_template("posts/edit_post.html", post=post)


    post.title = title
    post.category = category
    post.description = description
    db.session.commit()
    return redirect(url_for("posts.post_detail_page", post_id=post_id))


@posts_bp.route("/status_update/<int:post_id>", methods=["POST"])
@login_required
def status_update(post_id: int):
    post = db.session.get(Posts, post_id)
    if not post:
        return redirect(url_for("posts.my_posts"))

    if request.method == "GET":
        return render_template("posts/edit_post.html", post=post, cat_options=CATEGORY_OPTIONS)

    status = request.form.get("status")
    print(f"status - {status}")
    if not status:
        flash('Invalid status value. Please try again.', 'danger')
        return render_template("posts/edit_post.html", post=post)

    post.status = status
    db.session.commit()
    return redirect(url_for("posts.my_posts", post_id=post_id))
