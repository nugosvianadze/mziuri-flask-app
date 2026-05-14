from flask import (Flask, render_template,
                   request, url_for, redirect, session)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Table, Column, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_migrate import Migrate

import click
import sqlite3

from werkzeug.exceptions import NotFound

from utils.validators import validate_password, validate_email
from services.user_service import UserService


app = Flask(__name__)
migrate = Migrate()
CORS(app, resources={r"/api/*": {"origins": "http://localhost:63342"}})


DB_PATH = "mziuri.db"

user_service = UserService()

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SECRET_KEY"] = "NSDISUDUSBDUSBDIUB1h23ib12uibudusadbashidbasudbasiohio"

# initializations
db.init_app(app)
migrate.init_app(app, db)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    email: Mapped[str | None]
    password: Mapped[str | None]
    age: Mapped[int]

    posts: Mapped[list["Posts"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        uselist=False
    )

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "id": self.id,
            "email": self.email,
            "password": self.password
        }

    def to_dict_with_posts(self):
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "posts": [post.to_dict() for post in self.posts]
        }
        return data



class Posts(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None]
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(back_populates="posts")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)

    user: Mapped["User"] = relationship(back_populates="profile")

# many to many version 1

association_table = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)

    courses: Mapped[list["Course"]] = relationship(
        secondary=association_table,
        back_populates="students"
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)

    students: Mapped[list["Student"]] = relationship(
        secondary=association_table,
        back_populates="courses"
    )


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
    if not session.get("user_id"):
        return redirect(url_for("login"))
    users = db.session.scalars(db.select(User).limit(10)).all()
    return render_template("index.html", users=users)


@app.route("/api/posts/<int:user_id>", methods=["POST"])
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



# API endpoint
@app.route("/api/user_data", methods=["GET"])
def user_data():
    name = request.args.get("name")

    if name:
        users = user_service.get_users_with_word(name, db)
        return users
    return user_service.get_all_users(db, User)

@app.route("/api/user_data/<int:user_id>", methods=["GET"])
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
            "message": e
        }



@app.route("/api/user_data/<int:user_id>", methods=["PUT"])
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

@app.route("/api/user_posts/<int:user_id>")
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
            "message": e.description
        }, 500

@app.route("/login", methods=["GET", "POST"])
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
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("first_name", None)
    session.pop("last_name", None)
    return redirect(url_for("login"))

@app.route("/api/user_data/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int) -> tuple[dict, int]:
    data, status_code = user_service.delete_user(user_id, db, User)
    return data, status_code

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