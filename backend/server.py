import os
from flask import Flask, Blueprint, jsonify, request, make_response, g, redirect
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


@app.api.before_request
def before_request():
    g.db = get_db_session()
    session_cookie = request.cookies.get("ubcse_autolab_portal_session", "")
    g.user = Session.get_user(session_cookie)


@app.api.after_request
def after_request(response):
    g.db.close()
    return response


@app.api.route("/login/", methods=["GET", "POST"])
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
        user.first_name = first_name
        user.last_name = last_name
        g.db.commit()
    session, token = Session.create(user)
    resp = make_response(redirect("/portal"))
    resp.set_cookie("ubcse_autolab_portal_session", token, samesite="Strict", secure=True, httponly=True,
                    max_age=1735707600)
    return resp


@app.api.route("/logout/", methods=["POST"])
def logout():
    session_cookie = request.cookies.get("ubcse_autolab_portal_session", "")
    session = Session.get_session(session_cookie)
    if session is not None:
        session.logout()
    resp = make_response(redirect("/portal"))
    resp.set_cookie("ubcse_autolab_portal_session", "", samesite="Strict", secure=True, httponly=True, max_age=0)
    return resp


@app.api.route("/userinfo/")
def userinfo():
    if g.user is None:
        return jsonify({
            "success": False,
            "error": "You are not logged in."
        }), 401
    return jsonify({
        "success": True,
        "data": g.user.to_dict()
    })


@app.api.route("/my-courses/<string:username>/")
def my_courses(username: str):
    if g.user is None:
        return jsonify({
            "success": False,
            "error": "You are not logged in."
        }), 401
    if g.user.username != username and not g.user.is_admin:
        return jsonify({
            "success": False,
            "error": "You only authorized to view your own courses."
        }), 403
    professor = app.course_store.get_professors().get(username)
    if professor is None:
        return jsonify({
            "success": False,
            "error": f"{g.user.username} does not have any current or upcoming courses "
                     f"where they're the primary instructor."
        }), 403
    return jsonify({
        "success": True,
        "data": professor.to_dict()
    })


@app.api.route("/create-course/", methods=["POST"])
def create_course():
    if g.user is None:
        return jsonify({
            "success": False,
            "error": "You are not logged in."
        }), 401
    data = request.get_json()
    unique_course_identifier = data.get("uniqueIdentifier")
    course = app.course_store.get_by_unique_identifier(unique_course_identifier)
    if course is None:
        return jsonify({
            "success": False,
            "error": "Course not found."
        }), 404
    display_name = data.get("displayName")
    if display_name is None:
        return jsonify({
            "success": False,
            "error": "Missing required field: displayName"
        }), 400
    if g.user.username != course.instructor and not g.user.is_admin:
        return jsonify({
            "success": False,
            "error": "You are not the instructor of this course."
        }), 403

    instructor_email = course.instructor + "@buffalo.edu"
    technical_name = course.technical_name
    semester_code = course.semester_code

    try:
        app.autolab.create_course_automatic_dates(technical_name, display_name, semester_code, instructor_email)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to create course on Autolab. " + str(e),
        }), 500

    return jsonify({
        "success": True,
        "data": {
            "message": f"You successfully created the course {display_name}",
            "location": f"https://autolab.cse.buffalo.edu/courses/{course.technical_name}",
        }
    })


@app.api.route("/admin-update/", methods=["POST"])
def admin_update():
    # Checks if the user is an admin on Autolab. If so, make them an admin on the portal.
    # If they're already an admin on the portal, remove their admin status.
    if g.user is None:
        return jsonify({
            "success": False,
            "error": "You are not logged in."
        }), 401
    if g.user.is_admin:
        g.user.is_admin = False
        g.db.commit()
        return jsonify({
            "success": True,
            "isAdmin": False,
            "message": "You were already an admin, so we removed your admin status on the portal. "
                       "I guess you probably want to test something? You can always get it back by "
                       "clicking the button again. You may need to refresh the page to see the change."
        })
    try:
        is_autolab_admin = app.autolab.check_admin(g.user.email)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Failed to check admin status on Autolab. " + str(e),
        }), 500
    if is_autolab_admin:
        g.user.is_admin = True
        g.db.commit()
        return jsonify({
            "success": True,
            "isAdmin": True,
            "message": "We verified you're an admin on Autolab! You are now an admin on the portal. "
                       "You may need to refresh the page to see the change."
        })
    else:
        return jsonify({
            "success": False,
            "error": "Haha nice try! Did you think it was that easy? You are not an admin on Autolab, "
                     "so you can't be an admin here."
        }), 403


def initialize():
    # If, in the future, I want to use Alembic, remove this line:
    db.initialize()
    app.register_blueprint(app.api, url_prefix="/api")


initialize()

if __name__ == '__main__':
    app.run("0.0.0.0", 5057)
else:
    gunicorn_app = app
