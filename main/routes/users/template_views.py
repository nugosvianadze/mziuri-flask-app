import time

from flask import render_template, redirect, url_for, request, session
from flask_login import login_user, logout_user
from sqlalchemy import func, or_
from werkzeug.security import check_password_hash

from extensions import db, login_manager
from main import user_bp, login_required, get_user, Posts
from main.models.user import User

from services.auth_service import AuthService
from services.user_service import UserService
from utils.validators import validate_email

user_service = UserService()
auth_service = AuthService()


@login_manager.user_loader
def load_user(user_id):
    # Returns the User object or None if it doesn't exist
    return User.query.get(int(user_id))


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("user/login.html")
    email, password = request.form.get('email'), request.form.get('password')
    print(email, password)
    # password_validate = validate_password(password)
    email_validate = validate_email(email)

    # if not password_validate["success"] and password_validate["errors"]:
    #     return render_template("user/login.html", error=password_validate["errors"])

    if not email_validate["success"] and email_validate["errors"]:
        return render_template("user/login.html", error=email_validate["errors"])

    print(email, password)
    query = db.session.query(User).filter(User.email == email.strip())
    execute = db.session.execute(query)
    user = execute.scalar()
    if not user:
        print(1)
        return render_template("user/login.html",
                               error="Incorrect Credentials, Try again!")

    print(user.password)
    print(password)
    is_valid_password = check_password_hash(user.password, password)
    if not is_valid_password:
        print(2)
        return render_template("user/login.html",
                               error="Incorrect Credentials, Try again!")

    # session["user_id"] = user.id
    # session["first_name"] = user.first_name
    # session["last_name"] = user.last_name
    login_user(user)
    return redirect(url_for("home.home"))


@user_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("user/register.html")

    first_name, last_name, password, email, age = (request.form.get("first_name"),
                                                   request.form.get("last_name"),
                                                   request.form.get("password"),
                                                   request.form.get("email"),
                                                   request.form.get("age"))
    data: dict = auth_service.validate_signup_form(
        first_name, last_name, password, email, age
    )
    if data.get("errors"):
        return render_template("user/register.html", errors=data["errors"])

    data, status_code = user_service.create_user(db, User, first_name, last_name,
                                                 age, email, data["hashed_password"]["hash_password"])
    if not data.get("success"):
        return render_template("user/register.html", errors=[data.get('message')])

    login_user(data["user"])
    return redirect(url_for("home.home"))

@user_bp.route("/profile", methods=["GET"])
@login_required
def profile():
    total_views = db.session.query(func.sum(Posts.views_count)).filter(Posts.user_id == session["_user_id"]).scalar()
    return render_template("/user/profile.html", total_views=total_views)


@user_bp.route('/list', methods=["GET"])
@login_required
def user_list():
    q = request.args.get('q', None)
    if not q:
        users = db.session.execute(db.select(User).limit(10)).scalars()
    else:
        users = db.session.execute(
            db.select(User).where(
                or_(
                    User.first_name.ilike(f"%{q}%"),
                    User.last_name.ilike(f"%{q}%")
                )
            )
        ).scalars().all()
    return render_template("/user/users.html", users=users)



@user_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("users.login"))
