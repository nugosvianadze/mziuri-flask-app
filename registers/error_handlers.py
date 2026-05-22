from flask import redirect, url_for, Flask


def register_error_handlers(app: Flask):
    @app.errorhandler(404)
    def page_not_found(error):
        return redirect(url_for("home.home"))
