from flask import abort, current_app, jsonify
from flask import Blueprint, g

gat = Blueprint("gat", __name__)


def get_current_user_autolab_courses() -> dict:
    email_address = g.user.email
    autolab = current_app.autolab
    courses = autolab.user_courses(email_address)
    return courses


# Require login for all routes in this blueprint
@gat.before_request
def require_login():
    if g.user is None:
        abort(401)


@gat.route("/")
def index():
    return f"Hello from GAT (Grader Assignment Tool), {g.user.username}!"


@gat.route("/my-autolab-courses/")
def my_courses():
    courses = get_current_user_autolab_courses()
    return jsonify(courses)
