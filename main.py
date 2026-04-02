from flask import (Flask, render_template,
                   request, url_for, redirect)
from flask_cors import CORS

from services.validators import validate_password, validate_email
from services.user_service import UserService
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:63342"}})


@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("home"))

users = [
    {"id": 1, "first_name": "John", "last_name": "Doe", "age": 28},
    {"id": 2, "first_name": "Jane", "last_name": "Smith", "age": 34},
    {"id": 3, "first_name": "Michael", "last_name": "Johnson", "age": 45},
    {"id": 4, "first_name": "Olivia", "last_name": "Davis", "age": 22},
    {"id": 5, "first_name": "William", "last_name": "Brown", "age": 39},
    {"id": 6, "first_name": "Olivia", "last_name": "Wilson", "age": 27},
    {"id": 7, "first_name": "James", "last_name": "Taylor", "age": 31},
    {"id": 8, "first_name": "Sophia", "last_name": "Anderson", "age": 24},
    {"id": 9, "first_name": "Olivia", "last_name": "Thomas", "age": 36},
    {"id": 10, "first_name": "Isabella", "last_name": "Moore", "age": 29}
]


@app.route("/home", methods=["GET"])
@app.route("/")
def home():
    print(request.method)
    return render_template("index.html", users=users)


# API endpoint
@app.route("/api/user_data/<int:user_id>")
@app.route("/api/user_data")
def user_data(user_id: int = None):
    found_users = []

    first_name = request.args.get("first_name")

    if user_id is None and first_name is not None:
        UserService.get_users_with_word(first_name, users, found_users)

    elif user_id is not None and first_name is None:
        user = UserService.get_user_with_id(user_id, users)
        return user

    elif user_id and first_name:
        user = UserService.get_user_with_id(user_id, users)
        print(user)
        UserService.get_users_with_word(first_name, [user], found_users)
        print(found_users)
        return {
            'success': True,
            "users_data": found_users
        }, 200


    if not found_users and user_id:
        return {
            "success": False,
            "message": f"User with ID={user_id} not found!"
        }, 404
    elif not found_users and first_name:
        return {
            "success": False,
            "message": f"Users with first_name={first_name} not found!"
        }, 404
    return {
        "success": True,
        "message": found_users
    }, 200


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


@app.route('/test_args')
def test_args():
    print(request.args)
    print(request.args.get('arg1'))
    return request.args


if __name__ == "__main__":

    app.run(host="0.0.0.0", debug=True)