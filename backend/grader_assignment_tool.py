import cachetools.func
from typing import Tuple, Optional
from flask import abort, current_app, jsonify
from flask import Blueprint, g
from backend.models.gat_models import Course, CourseUser, CourseConflictOfInterest, CourseGradingAssignment, \
    CourseGradingAssignmentPair

gat = Blueprint("gat", __name__)


def get_current_user_autolab_courses() -> dict:
    email_address = g.user.email
    autolab = current_app.autolab
    courses = autolab.user_courses(email_address)
    return courses


@cachetools.func.ttl_cache(maxsize=100, ttl=60)
def user_is_grader_in_autolab_course(user_email: str, course_name: str) -> Tuple[bool, Optional[dict]]:
    # Returns true if the user is an instructor or CA in the course on Autolab, false otherwise
    # If true, also return the course information dict
    autolab = current_app.autolab
    user_courses: dict = autolab.user_courses(user_email)
    for course in user_courses["courses"]:
        if course["name"] == course_name:
            if course["role"] == "instructor" or course["role"] == "course_assistant":
                return True, course
            break
    return False, None


# Require login for all routes in this blueprint
@gat.before_request
def require_login():
    if g.user is None:
        abort(401)


@gat.route("/")
def index():
    return f"Hello from GAT (Grader Assignment Tool), {g.user.username}!"


@gat.route("/my-autolab-courses/", methods=["GET"])
def my_autolab_courses():
    courses = get_current_user_autolab_courses()
    return jsonify(courses)


@gat.route("/create-course/<course_name>/", methods=["POST"])
def create_course(course_name: str):
    # Given an Autolab course name, create a corresponding course in our database, if the user has permission
    in_course: bool
    course_info: Optional[dict]
    in_course, course_info = user_is_grader_in_autolab_course(g.user.email, course_name)
    if not in_course:
        abort(403, "You are not an instructor or course assistant in this course on Autolab")

    # Check if the course already exists in our database
    course = g.db.query(Course).filter_by(name=course_name).first()
    if course is not None:
        abort(400, "This course has already been created")

    display_name = f"{course_info['display_name']} ({course_info['semester']})"
    technical_name = course_info["name"]

    # Create the course in our database
    course = Course(name=technical_name, display_name=display_name, created_by_user=g.user)
    g.db.add(course)
    g.db.commit()

    return jsonify({
        "success": True,
        "data": course.to_dict()
    })
