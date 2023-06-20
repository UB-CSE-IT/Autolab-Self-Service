import os

from flask import Flask, Blueprint, jsonify, request, make_response
from dotenv import load_dotenv

from backend import db
from backend.connections.AutolabApiConnection import AutolabApiConnection
from backend.connections.InfosourceConnection import InfoSourceConnection
from backend.CourseStore import CourseStore
from backend.db import get_db_session
from backend.models.session import Session
from backend.models.user import User

load_dotenv()
app = Flask(__name__)
app.api = Blueprint("api", __name__)
app.autolab = AutolabApiConnection(os.getenv("AUTOLAB_ROOT"), os.getenv("AUTOLAB_CLIENT_ID"),
                                   os.getenv("AUTOLAB_CLIENT_SECRET"), os.getenv("AUTOLAB_CLIENT_CALLBACK"))
app.infosource = InfoSourceConnection(os.getenv("INFOSOURCE_USERNAME"),
                                      os.getenv("INFOSOURCE_PASSWORD"), os.getenv("INFOSOURCE_DSN"))
app.course_store = CourseStore(app.infosource)


@app.api.route("/login/")
def login():
    username = request.headers.get("Uid")
    person_number = request.headers.get("Pn")
    first_name = request.headers.get("Givenname")
    last_name = request.headers.get("Sn")
    if not all([username, person_number, first_name, last_name]):
        return jsonify({
            "success": False,
            "error": "Missing required headers from Shibboleth."
        }), 400
    user = User.get_by_username(username)
    if user is None:
        user = User.create(username, first_name, last_name, person_number)
    user.login()
    if user.first_name != first_name or user.last_name != last_name:
        # Update the user's name if it has changed
        with get_db_session() as db:
            user.first_name = first_name
            user.last_name = last_name
            db.commit()
    session, token = Session.create(user)
    ret = {
        "success": True,
        "data": {
            "username": user.username,
            "person_number": user.person_number,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    }
    resp = make_response(jsonify(ret))
    resp.set_cookie("ubcse_autolab_portal_session", token, samesite="Strict", secure=True, httponly=True,
                    max_age=1735707600)
    return resp


@app.api.route("/my-courses/<string:username>/")
def my_courses(username: str):
    return jsonify(app.course_store.get_professors().get(username).to_dict())


def main():
    # If, in the future, I want to use Alembic, remove this line:
    db.initialize()
    app.register_blueprint(app.api, url_prefix="/api")
    app.run("0.0.0.0", 5057)


if __name__ == '__main__':
    main()
