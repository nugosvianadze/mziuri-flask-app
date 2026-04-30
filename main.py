from flask import (Flask, render_template,
                   request, url_for, redirect)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import click
import sqlite3

from utils.validators import validate_password, validate_email
from services.user_service import UserService


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:63342"}})


DB_PATH = "mziuri.db"

user_service = UserService()

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
db.init_app(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    age: Mapped[int]

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age
        }


class Posts(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory =  sqlite3.Row
    return conn

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("home"))


@app.route("/home", methods=["GET"])
@app.route("/")
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from users")
    users = cursor.fetchall()
    conn.close()
    return render_template("index.html", users=users)


# API endpoint
@app.route("/api/user_data", methods=["GET"])
def user_data():
    name = request.args.get("name")

    if name:
        users = user_service.get_users_with_word(name, db)
        return users
    return user_service.get_all_users()

@app.route("/api/user_data/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    try:
        data = user_service.get_user_with_id(user_id)
        return data
    except Exception as e:
        return {
            "success": False,
            "message": e
        }



@app.route("/api/user_data/<int:user_id>", methods=["PUT"])
def update_user_data(user_id: int):
    data = request.json
    if user_id and isinstance(user_id, int):
        data = user_service.update_user(user_id, data)
        return data
    return {
        "success": False,
        "message": "user id param is not valid, try again!",
        "data": None
    }
#
#
# @app.route("/api/user_data/<int:user_id>", methods=["PATCH"])
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

@app.route("/api/user_data", methods=["POST"])
def create_user():
    """

    {"first_name": "nugo"}
    """
    data = request.json
    if data:
        try:

            first_name, last_name, age = (data.get("first_name"),
                                          data.get("last_name"), data.get("age"))
            user = User(
                first_name=first_name,
                last_name=last_name,
                age=age
            )
            db.session.add(user)
            db.session.commit()
            return {
                "success": True,
                "message": "User Successfully Created!",
                "data": {
                    "first_name": first_name
                }
            }
        except Exception as e:
            print('Error', e)
            db.session.rollback()
    return {
        "success": False,
        "message": "Data is not provided!",
        "data": None
    }

@app.route("/login", methods=["GET", "POST"])
def login():
    test_user_data = {
        'email': "test@gmail.com",
        'password': "123456"
    }
    if request.method == "GET":
        return render_template("login.html")
    email, password = request.form.get('email'), request.form.get('password')

    password_validate = validate_password(password)
    email_validate = validate_email(email)

    if not password_validate["success"] and password_validate["errors"]:
        return render_template("login.html", errors=password_validate["errors"])

    if not email_validate["success"] and email_validate["errors"]:
        return render_template("login.html", errors=email_validate["errors"])

    if email == test_user_data['email'] and password != test_user_data['password']:
        return render_template("login.html",
                               error="Password doesnt match!")
    if email != test_user_data['email']:
        return render_template("login.html",
                               error="Account with this email doesnt exist!")
    if email == test_user_data['email'] and password == test_user_data["password"]:
        return redirect(url_for("home"))

@app.route("/api/user_data/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int) -> dict:
    data = user_service.delete_user(user_id)
    return data

@app.route('/test_args')
def test_args():
    print(request.args)
    print(request.args.get('arg1'))
    return request.args


@app.cli.command("init-db")
def init_db_command():
    db.create_all()
    click.echo("Database initialized.")

@app.cli.command("drop-all-tables")
def drop_all_tables():
    db.drop_all()
    click.echo("Database cleared!")


if __name__ == "__main__":


    app.run(host="0.0.0.0", debug=True)