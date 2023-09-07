import logging
import cachetools.func
from typing import Tuple, Optional, List, Dict, Any

from flask import abort, current_app, jsonify, request
from flask import Blueprint, g

from backend.connections.autolab_api_connection import AutolabApiConnection
from backend.models.gat_models import CourseRole
from backend.per_user_rate_limiter import rate_limit_per_user
import backend.grader_assignment_tool as gat

logger = logging.getLogger("portal")

cs = Blueprint("course_sections", __name__)


@cachetools.func.ttl_cache(maxsize=100, ttl=60)
def user_is_instructor_in_autolab_course(user_email: str, course_name: str) -> Tuple[bool, Optional[dict]]:
    # Returns a tuple with true if the user is an instructor in the course on Autolab, false otherwise
    # If true, also return the course information dict
    return gat.user_has_role_in_autolab_course(user_email, course_name, [CourseRole.INSTRUCTOR])


def ensure_current_user_is_instructor_in_autolab_course(course_name) -> dict:
    # Returns course dict if the user is an instructor in the course on Autolab
    # Immediately aborts with 403 if the user is not an instructor in the course on Autolab
    is_instructor, course_info = user_is_instructor_in_autolab_course(g.user.email, course_name)
    if not is_instructor and not g.user.is_admin:
        abort(403, "You are not an instructor in this course on Autolab.")
    return course_info


# Require login for all routes in this blueprint
@cs.before_request
def require_login():
    if g.user is None:
        abort(401)


@cs.route("/")
def index_view():
    return f"Hello from the course sections API, {g.user.username}!"


@cs.route("/<course_name>/", methods=["GET"])
@rate_limit_per_user(5, 5)  # 5 requests per 5 seconds
def get_course_sections(course_name: str):
    course: dict = ensure_current_user_is_instructor_in_autolab_course(course_name)
    autolab: AutolabApiConnection = current_app.autolab
    sections = autolab.get_course_sections(course_name)

    return jsonify({
        "success": True,
        "data": {
            "course": course,
            "sections": sections["sections"],
        }
    })


@cs.route("/<course_name>/", methods=["POST"])
@rate_limit_per_user(1, 2)  # 1 request per 2 seconds
def upsert_course_sections(course_name: str):
    # POST body should be a list of sections like:
    # [
    #   {
    #     "days_code": 42,
    #     "start_time": "13:00:00",
    #     "end_time": "16:00:00",
    #     "name": "Auto1",
    #     "is_lecture": True,
    #   },...
    # ]
    ensure_current_user_is_instructor_in_autolab_course(course_name)
    sections: List[Dict[str, Any]] = request.get_json()
    autolab: AutolabApiConnection = current_app.autolab
    autolab.upsert_course_sections(course_name, sections)

    return jsonify({
        "success": True,
    })
