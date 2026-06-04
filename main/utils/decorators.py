from functools import wraps
import time

from flask import session, url_for
from werkzeug.utils import redirect


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"gamovidzaxet dekoratori funkciistvis {func.__name__}, argumentebit {args}-{kwargs}")
        if "user_id" not in session:
            print("useri ar aris daloginebuli")
            return redirect(url_for("users.login"))
        print('useri daloginebulia')
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"funkcias dachirda {end_time - start_time}")
        return result

    return wrapper

