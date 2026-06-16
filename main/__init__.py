import os

from flask import Flask
from flask_cors import CORS

from registers.error_handlers import register_error_handlers
from extensions import db, migrate, login_manager

from main.routes import *
from main.routes.posts.template_views import *
from main.routes.posts.api import *

from main.routes.users.api import *
from main.routes.users.template_views import *
from registers.security import register_sec


# Static template routes (commented out for now)
# @main.route("/profile")
# def profile_page():
#     return render_template("profile.html")
#
# @main.route("/my-posts")
# def my_posts_page():
#     return render_template("my_posts.html")
#
# @main.route("/create-post")
# def create_post_page():
#     return render_template("create_post.html")
#
# @main.route("/search")
# def search_results_page():
#     return render_template("search_results.html")
#
# @main.route("/register")
# def register_page():
#     return render_template("register.html")
#


# Placeholder routes for publish workflow
# @main.route("/post/<int:post_id>/publish", methods=["POST"])
# def publish_post(post_id: int):
#     return {
#         "success": True,
#         "message": f"Post {post_id} published (placeholder)"
#     }

# @main.route("/post/<int:post_id>/draft", methods=["POST"])
# def mark_post_as_draft(post_id: int):
#     return {
#         "success": True,
#         "message": f"Post {post_id} moved to draft (placeholder)"
#     }

# @main.route("/post/<int:post_id>/edit", methods=["GET"])
# def edit_post_page(post_id: int):
#     return render_template("edit_post.html")

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_object('config.Config')
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:63342"}})


    app.register_blueprint(user_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(main_bp)
    # sec = register_sec(db, app)
    print(app.blueprints["posts"].view_functions)

    register_error_handlers(app)
    # register_commands(main, db)
    print(app)
    return app
