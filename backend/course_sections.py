import logging
from datetime import datetime

import cachetools.func
from typing import Tuple, Optional, List, Dict, Any

from flask import abort, current_app, jsonify, request
from flask import Blueprint, g

from backend.connections.autolab_api_connection import AutolabApiConnection
from backend.connections.infosource_connection import InfoSourceConnection
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


def validate_sections(sections: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    # Validate that sections are reasonable. Return a Tuple with a list of valid sections and a list of errors
    errors: List[str] = []
    valid_sections: List[Dict[str, Any]] = []
    for section in sections:
        section_name = section.get("name", "[Unnamed Section]")
        if section_name == "":
            # Ignore empty section names
            continue
        is_lecture = section.get("is_lecture", None)
        if is_lecture is None:
            errors.append(f"{section_name} is missing is_lecture")
            continue
        elif not isinstance(is_lecture, bool):
            errors.append(f"{section_name} is_lecture must be a boolean")
            continue
        section_type: str = "Lecture" if is_lecture else "Section"
        start_time = section.get("start_time", None)
        if start_time is None:
            errors.append(f"{section_type} \"{section_name}\" is missing start_time")
            continue
        if not isinstance(start_time, str):
            errors.append(f"{section_type} \"{section_name}\" start time must be a string")
            continue
        try:
            start_time_dt = datetime.strptime(start_time, "%H:%M:%S")
        except ValueError:
            errors.append(f"{section_type} \"{section_name}\" start time must be a valid time formatted as 20:30:40")
            continue
        end_time = section.get("end_time", None)
        if end_time is None:
            errors.append(f"{section_type} \"{section_name}\" is missing end_time")
            continue
        if not isinstance(end_time, str):
            errors.append(f"{section_type} \"{section_name}\" end time must be a string")
            continue
        try:
            end_time_dt = datetime.strptime(end_time, "%H:%M:%S")
        except ValueError:
            errors.append(f"{section_type} \"{section_name}\" end time must be a valid time formatted as 20:30:40")
            continue
        if start_time_dt >= end_time_dt:
            errors.append(f"{section_type} \"{section_name}\" start time must be before end time")
            continue
        days_code = section.get("days_code", None)
        if days_code is None:
            errors.append(f"{section_type} \"{section_name}\" is missing days code")
            continue
        if not isinstance(days_code, int):
            errors.append(f"{section_type} \"{section_name}\" days code must be an integer")
            continue
        if days_code < 0 or days_code > 127:
            errors.append(f"{section_type} \"{section_name}\" days code must be between 0 and 127")
            continue
        valid_sections.append({
            "name": section["name"],
            "is_lecture": section["is_lecture"],
            "start_time": section["start_time"],
            "end_time": section["end_time"],
            "days_code": section["days_code"],
        })

    return valid_sections, errors


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
    # POST body should be a dict with a list of sections like:
    # {
    #   "sections": [
    #     {
    #       "days_code": 42,
    #       "start_time": "13:00:00",
    #       "end_time": "16:00:00",
    #       "name": "Auto1",
    #       "is_lecture": True,
    #     },...
    #   ]
    # }
    ensure_current_user_is_instructor_in_autolab_course(course_name)
    sections: List[Dict[str, Any]] = request.get_json().get("sections", [])

    valid_sections: List[Dict[str, Any]]
    errors: List[str]
    valid_sections, errors = validate_sections(sections)

    if len(errors) > 0:
        return jsonify({
            "success": False,
            "error": "There were errors in the sections you provided. Nothing has been updated. Here are the details:",
            "errors": errors,
        }), 400

    if len(valid_sections) == 0:
        return jsonify({
            "success": False,
            "error": "No sections were updated.",
        }), 400

    autolab: AutolabApiConnection = current_app.autolab
    autolab.upsert_course_sections(course_name, valid_sections)

    return jsonify({
        "success": True,
    })


@cs.route("/<course_name>/import/", methods=["POST"])
@rate_limit_per_user(1, 7)  # 1 request per 7 seconds
def import_infosource_course_sections(course_name: str):
    # Find and import course sections from InfoSource
    ensure_current_user_is_instructor_in_autolab_course(course_name)
    autolab: AutolabApiConnection = current_app.autolab
    infosource: InfoSourceConnection = current_app.infosource
    try:
        sections: List[Dict[str, Any]] = infosource.get_course_sections_by_autolab_course_name(course_name)
    except Exception as e:
        logger.error(f"Error getting course sections from InfoSource: {e}")
        return jsonify({
            "success": False,
            "error": "An error occurred while querying the UB database. This course may not exist in the UB database.",
        }), 500

    if len(sections) == 0:
        return jsonify({
            "success": False,
            "error": "No sections were found for this course in the UB database.",
        }), 400

    autolab.upsert_course_sections(course_name, sections)

    return jsonify({
        "success": True,
    })
