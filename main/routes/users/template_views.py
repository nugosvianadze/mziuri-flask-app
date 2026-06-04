from flask import render_template, redirect, url_for, request, session
from werkzeug.security import check_password_hash

from extensions import db
from main import user_bp
from main.models.user import User
from services.auth_service import AuthService
from services.user_service import UserService
from utils.validators import validate_email

user_service = UserService()
auth_service = AuthService()


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

    session["user_id"] = user.id
    session["first_name"] = user.first_name
    session["last_name"] = user.last_name
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

    session["user_id"] = data["data"]["id"]
    session["email"] = data["data"]["email"]
    return redirect(url_for("home.home"))


@user_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("email", None)
    return redirect(url_for("users.login"))
