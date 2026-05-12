import sqlite3

from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound

from config import DB_PATH

class UserService:

    # @staticmethod
    # def _get_db():
    #     conn = sqlite3.connect(DB_PATH)
    #     conn.row_factory = sqlite3.Row
    #     return conn


    def get_users_with_word(self, name: str, db: SQLAlchemy):
        from main import User

        data = {}
        if name is not None:
            query = db.session.query(User).filter(User.first_name.like(f"%{name}%") | User.last_name.like(f"%{name}%"))
            result = db.session.execute(query)
            result = result.scalars().all()
            result = [user.to_dict() for user in result]
            data = {"success": True, "data": result}
        if data:
            return data
        return {"success": False, "data": []}

    def get_all_users(self, db, user):
        try:
            users = db.session.execute(db.select(user).limit(10)).scalars().all()
            users_dict = [user.to_dict() for user in users]
            return {
                "success": True,
                "data": users_dict
            }
        except Exception as e:
            return {
                "success": False,
                "message": e
            }

    @staticmethod
    def get_user_with_id(db: SQLAlchemy, user_cls, u_id: int) -> dict | None:
        user = db.get_or_404(user_cls, u_id)
        print(user)
        if user:
            return {
                "success": True,
                "user": user
            }
        return {
            "success": False,
            "message": f"User with id={u_id} was not found!"
        }

    def update_user(self, user_id: int, data, db: SQLAlchemy, user_cls):
        return_data = {}
        try:
            user = db.get_or_404(user_cls, user_id)
        except NotFound as e:
            return {
            "success": False,
            "message": f"User with id={user_id}, not found!"
        }, 404
        if user:

            first_name, last_name, age = (data.get("first_name"), data.get("last_name"),
                                          data.get("age"))
            is_all_provided = all([first_name, last_name, age])
            if is_all_provided:
                user.first_name = first_name
                user.last_name = last_name
                user.age = age
                db.session.commit()
                return_data = {
                    "success": True,
                    "message": "User Successfully updated!",
                    "data": user.to_dict()
                }, 200
            else:
                return_data = {
                    "success": False,
                    "message": "Wrong paramaters, mandatory fields : first_name, last_name, age "
                }, 400
        if return_data:
            return return_data, 200


    @staticmethod
    def delete_user(user_id: int, db: SQLAlchemy, user_cls) -> tuple[dict, int]:
        try:
            user = db.get_or_404(user_cls, user_id)
        except NotFound as e:
            return {
            "success": False,
            "message": f"User with id={user_id}, not found!"
        }, 404

        try:
            db.session.delete(user)
            db.session.commit()
            return {
                "success": True,
                "message": f"User with id={user_id} deleted successfully!"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": e
            }, 500

    @staticmethod
    def create_user(db, user_cls, first_name: str,
                    last_name: str, age: int) -> tuple[dict, int]:
        if not age:
            return {
                "success": False,
                "message": "Age field is required!"
            }, 400

        if not isinstance(first_name, str) or not isinstance(last_name, str):
            return {
                "success": False,
                "message": "First name or Last name field must be string type"
            }, 400

        try:
            user = user_cls(
            first_name=first_name,
            last_name=last_name,
            age=age
            )
            db.session.add(user)
            db.session.commit()
            return {
                "success": True,
                "message": "User Successfully Created!",
                "data": user.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "message": e
            }, 500