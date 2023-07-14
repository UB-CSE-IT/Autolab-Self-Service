import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, Blueprint, jsonify, request, make_response, g, redirect, abort
from dotenv import load_dotenv
from backend import db
from backend.PerUserRateLimiter import rate_limit_per_user
from backend.connections.AutolabApiConnection import AutolabApiConnection
from backend.connections.InfosourceConnection import InfoSourceConnection
from backend.CourseStore import CourseStore
from backend.connections.TangoApiConnection import TangoApiConnection
from backend.db import get_db_session
from backend.models.session import Session
from backend.models.user import User
from backend.utils import get_client_ip

logger = logging.getLogger("portal")
load_dotenv()
app = Flask(__name__)
app.request_counter = 0
app.api = Blueprint("api", __name__)
app.user_api = Blueprint("user_api", __name__)
app.autolab = AutolabApiConnection(os.getenv("AUTOLAB_ROOT"), os.getenv("AUTOLAB_CLIENT_ID"),
                                   os.getenv("AUTOLAB_CLIENT_SECRET"), os.getenv("AUTOLAB_CLIENT_CALLBACK"))
app.tango = TangoApiConnection(os.getenv("TANGO_HOST"), os.getenv("TANGO_KEY"), float(os.getenv("TANGO_MAX_POLL_RATE")))
app.infosource = InfoSourceConnection(os.getenv("INFOSOURCE_USERNAME"),
                                      os.getenv("INFOSOURCE_PASSWORD"), os.getenv("INFOSOURCE_DSN"))
app.course_store = CourseStore(app.infosource)
app.developer_mode = os.getenv("DEVELOPER_MODE", "").lower() == "true"


def init_logging():
    class RequestContextFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            # Pad the level name for consistent indentation
            record.levelname = f"[{record.levelname}]".rjust(10)

            # Tag each log message with the request ID since they can be concurrent
            try:
                record.request_id = str(g.request_number)
            except (AttributeError, RuntimeError):
                record.request_id = "------"  # This length matches the padding of 6 below to avoid prefixing it with 0s
            record.request_id = f"R#{record.request_id.rjust(6, '0')}".rjust(8)

            # Indent all log messages except the first one in a request
            try:
                record.indent = g.request_initiated * "    "
            except (AttributeError, RuntimeError):
                record.indent = ""
            return True

    os.makedirs("mount/logs", exist_ok=True)
    logger.setLevel(logging.DEBUG if app.developer_mode else logging.INFO)
    handler = RotatingFileHandler("mount/logs/portal.log", maxBytes=10_000_000, backupCount=5_000)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(request_id)s%(indent)s %(message)s (%(module)s)")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addFilter(RequestContextFilter())
    logger.debug("Logging initialized")


@app.api.before_request
def before_request():
    app.request_counter += 1
    g.request_initiated = False
    g.request_number = app.request_counter
    g.db = get_db_session()
    session_cookie = request.cookies.get("ubcse_autolab_portal_session", "")
    g.user = Session.get_user(session_cookie)
    logger.info(
        f"Beginning request #{g.request_number} {request.method} {request.path} "
        f"from {g.user.username if g.user else '(unknown user)'} "
        f"at {get_client_ip(request)}")
    g.request_initiated = True


@app.api.after_request
def after_request(response):
    g.db.close()
    if response.json and response.json.get("error"):
        logger.info(f"Error: {response.json['error']}")
    logger.info(f"Finished request #{g.request_number} with status {response.status}")
    return response


@app.api.route("/login/", methods=["GET", "POST"])
def login():
    username = request.headers.get("Uid")
    person_number = request.headers.get("Pn")
    first_name = request.headers.get("Givenname")
    last_name = request.headers.get("Sn")
    if not all([username, person_number, first_name, last_name]):
        logger.warning(f"Missing required headers from Shibboleth. In production, there's either a misconfiguration or "
                       f"a user is accessing portal directly, which would be a security issue.")
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
        logger.info(f"Updating user {user.username} with new name from Shibboleth {first_name} {last_name}")
        user.first_name = first_name
        user.last_name = last_name
        g.db.commit()
    session, token = Session.create(user)
    resp = make_response(redirect("/portal"))
    resp.set_cookie("ubcse_autolab_portal_session", token, samesite="Strict", secure=True, httponly=True,
                    max_age=1735707600)
    logger.info(f"User {user.username} logged in successfully")
    return resp


@app.api.route("/login/dev/", methods=["POST"])
def dev_login():
    if not app.developer_mode:
        logger.warning(f"Attempted to use developer login when developer mode is not enabled")
        return jsonify({
            "success": False,
            "error": "Developer mode is not enabled."
        }), 403

    username = request.form.get("username")
    user_data = app.infosource.get_person_info_by_username(username)
    if user_data is None:
        return jsonify({
            "success": False,
            "error": "User does not exist."
        }), 404

    first_name = user_data["FIRST_NAME"]
    last_name = user_data["LAST_NAME"]
    person_number = user_data["PERSON_NUMBER"]

    # Set the headers as if they came from Shibboleth to pass to the regular login
    request.headers.environ["HTTP_UID"] = username
    request.headers.environ["HTTP_PN"] = person_number
    request.headers.environ["HTTP_GIVENNAME"] = first_name
    request.headers.environ["HTTP_SN"] = last_name

    # Call the regular login
    logger.info(f"Developer login for {username} initiated. Passing through to regular login.")
    return login()


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
# Cannot be rate limited because it is used to check if the user is logged in
def userinfo():
    if g.user is None:
        return jsonify({
            "success": False,
            "error": "You are not logged in.",
            "developerMode": app.developer_mode,
        }), 401
    return jsonify({
        "success": True,
        "data": g.user.to_dict(),
        "developerMode": app.developer_mode,
    })


@app.api.route("/my-courses/<string:username>/")
@rate_limit_per_user(5, 5)  # 5 request per 5 seconds. This one isn't very computationally expensive
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
    professors = app.course_store.get_professors()
    logger.debug(f"Found {len(professors)} professors")
    logger.debug(f"Looking for {username}")
    professor = professors.get(username)
    if professor is None:
        logger.info(f"Could not find {username} in the list of professors")
        return jsonify({
            "success": False,
            "error": f"{username} does not have any current or upcoming courses "
                     f"where they're the primary instructor."
        }), 404
    logger.info(f"Found {len(professor.courses)} courses for {username}")
    return jsonify({
        "success": True,
        "data": professor.to_dict()
    })


@app.api.route("/create-course/", methods=["POST"])
@rate_limit_per_user(1, 5)  # 1 request per 5 seconds
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
@rate_limit_per_user(10, 60)  # 10 requests per minute
@rate_limit_per_user(3, 5)  # 3 requests per 5 seconds
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
        logger.info(f"User {g.user.username} is no longer an admin on the portal")
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
        logger.info(f"User {g.user.username} is now an admin on the portal")
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


@app.user_api.before_request
def user_api_before_request():
    app.request_counter += 1
    g.request_initiated = False
    g.request_number = app.request_counter
    if request.headers.get("Authorization", None) != os.getenv("USER_API_KEY"):
        abort(403)
    g.db = get_db_session()
    logger.debug(
        f"Beginning request #{g.request_number} {request.method} {request.path} "
        f"from USER API "
        f"at {get_client_ip(request)}")
    g.request_initiated = True


@app.user_api.after_request
def user_api_after_request(response):
    if hasattr(g, "db"):
        # If the request was aborted, the db session won't exist
        g.db.close()
    logger.debug(f"Finished request #{g.request_number} with status {response.status}")
    return response


@app.user_api.route("/tango_histogram/", methods=["GET"])
def tango_histogram():
    return jsonify(app.tango.get_recent_submissions_histogram())


def initialize():
    with app.app_context():
        init_logging()
    # If, in the future, I want to use Alembic, remove this line:
    db.initialize()
    app.register_blueprint(app.api, url_prefix="/api")
    app.register_blueprint(app.user_api, url_prefix="/api/user_api")


initialize()

if __name__ == '__main__':
    logger.info("Initializing Flask development server")
    app.run("0.0.0.0", 5057)
else:
    logger.info("Initializing Gunicorn production server")
    gunicorn_app = app
