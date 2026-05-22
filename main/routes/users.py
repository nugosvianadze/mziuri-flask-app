from flask import Blueprint, render_template, redirect, url_for, request, session

from main.models.user import User
from extensions import db
from services.user_service import UserService
from utils.validators import validate_password, validate_email

user_bp = Blueprint("users", __name__, url_prefix="/api/user_data")
user_service = UserService()

@user_bp.route("/", methods=["GET"])
def user_data():
    name = request.args.get("name")

    if name:
        users = user_service.get_users_with_word(name, db)
        return users
    return user_service.get_all_users(db, User)


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    try:
        u_data = user_service.get_user_with_id(db, User, user_id)
        if u_data:
            return {
                "success": u_data["success"],
                "data": u_data["user"].to_dict()
            }
    except Exception as e:
        return {
            "success": False,
            "message": e.description
        }


@user_bp.route("/api/user_data/<int:user_id>", methods=["PUT"])
def update_user_data(user_id: int):
    data = request.json
    if user_id and isinstance(user_id, int):
        data, status_code = user_service.update_user(user_id, data, db, User)
        return data, status_code
    return {
        "success": False,
        "message": "user id param is not valid, try again!",
        "data": None
    }, 404


@user_bp.route("/api/user_data", methods=["POST"])
def create_user():
    """

    {"first_name": "nugo"}
    """
    data = request.json
    if data:
        data, status_code = user_service.create_user(db,
                                                     User,
                                                     data.get("first_name"),
                                                     data.get("last_name"),
                                                     data.get("age"))

        return data, status_code
    return {
        "success": False,
        "message": "Data is not provided!",
        "data": None
    }


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    email, password = request.form.get('email'), request.form.get('password')

    password_validate = validate_password(password)
    email_validate = validate_email(email)

    if not password_validate["success"] and password_validate["errors"]:
        return render_template("login.html", errors=password_validate["errors"])

    if not email_validate["success"] and email_validate["errors"]:
        return render_template("login.html", errors=email_validate["errors"])

    users = db.session.execute(db.select(User).limit(10)).scalars().all()
    users_dict = [user.to_dict() for user in users]
    print(users_dict)
    print(email, password)
    query = db.session.query(User).filter(User.email == email.strip(),
                                          User.password == password.strip())
    execute = db.session.execute(query)
    user = execute.scalar()
    print(user)
    if not user:
        return render_template("login.html",
                               error="Incorrect Credentials, Try again!")
    session["user_id"] = user.id
    session["first_name"] = user.first_name
    session["last_name"] = user.last_name
    return redirect(url_for("home.home"))


@user_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("first_name", None)
    session.pop("last_name", None)
    return redirect(url_for("users.login"))


@user_bp.route("/api/user_data/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int) -> tuple[dict, int]:
    data, status_code = user_service.delete_user(user_id, db, User)
    return data, status_code

#
#
# @user_bp.route("/api/user_data/<int:user_id>", methods=["PATCH"])
# def partial_update_user_data(user_id: int):
#     data = request.json
#     method = request.method
#     if user_id and isinstance(user_id, int):
#         user = UserService.get_user_with_id(user_id, users)
#         first_name, last_name, age = (data.get("first_name"), data.get("last_name"),
#                                       data.get("age"))
#         if user is not None:
#             for usr in users:
#                 if user_id == usr["id"]:
#                     usr["first_name"] = first_name if first_name else usr["first_name"]
#                     usr["last_name"] = last_name if last_name else usr["last_name"]
#                     usr["age"] = age if age else usr["age"]
#
#                     return {
#                         "success": True,
#                         "message": f"User with id {user_id} successfully deleted",
#                         "data": users
#                     }
#
#         return {
#             "success": False,
#             "message": f"User with id {user_id} was not found!",
#             "data": None
#         }
#     return {
#         "success": False,
#         "message": "user id param is not valid, try again!",
#         "data": None
#     }
