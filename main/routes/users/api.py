from flask import request

from extensions import db
from main import user_bp
from main.models.user import User
from services.auth_service import AuthService
from services.user_service import UserService

user_service = UserService()
auth_service = AuthService()


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


@user_bp.route("/api/user_data/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int) -> tuple[dict, int]:
    data, status_code = user_service.delete_user(user_id, db, User)
    return data, status_code

