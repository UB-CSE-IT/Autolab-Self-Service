from flask import abort

from flask import Blueprint, g

gat = Blueprint("gat", __name__)


# Require login for all routes in this blueprint
@gat.before_request
def require_login():
    if g.user is None:
        abort(401)


@gat.route("/")
def index():
    return f"Hello from GAT, {g.user.username}!"
