import logging

import cachetools.func
from typing import Tuple, Optional, List, Sequence, Set, Dict

from flask import abort, current_app, jsonify
from flask import Blueprint, g

from backend.models.gat_models import Course, CourseUser, CourseConflictOfInterest, CourseGradingAssignment, \
    CourseGradingAssignmentPair, CourseRole
from backend.models.user import User

logger = logging.getLogger("portal")

gat = Blueprint("gat", __name__)


def get_current_user_autolab_courses() -> dict:
    email_address = g.user.email
    autolab = current_app.autolab
    courses = autolab.user_courses(email_address)
    return courses


def string_to_course_role(role_string: str) -> CourseRole:
    role_string = role_string.lower()
    if role_string == "instructor":
        return CourseRole.INSTRUCTOR
    elif role_string == "course_assistant":
        return CourseRole.TA
    elif role_string == "student":
        return CourseRole.STUDENT
    else:
        raise ValueError(f"Invalid role string: {role_string}")


def course_role_to_string(role: CourseRole) -> str:
    if role == CourseRole.INSTRUCTOR:
        return "instructor"
    elif role == CourseRole.TA:
        return "course_assistant"
    elif role == CourseRole.STUDENT:
        return "student"
    else:
        raise ValueError(f"Invalid role: {role}")


@cachetools.func.ttl_cache(maxsize=100, ttl=60)
def user_is_grader_in_autolab_course(user_email: str, course_name: str) -> Tuple[bool, Optional[dict]]:
    # Returns true if the user is an instructor or CA in the course on Autolab, false otherwise
    # If true, also return the course information dict
    # This should only be used for initially creating the local course and syncing the roster with Autolab
    # Local course operations should use `user_is_grader_in_course`
    autolab = current_app.autolab
    user_courses: dict = autolab.user_courses(user_email)
    for course in user_courses["courses"]:
        if course["name"] == course_name:
            if string_to_course_role(course["role"]) in [CourseRole.INSTRUCTOR, CourseRole.TA]:
                return True, course
            break
    return False, None


def get_grader_courses(user: User) -> List[Course]:
    # Returns a list of all courses that the user is an instructor or CA in
    if user.is_admin:
        return list(g.db.query(Course).all())

    course_users = g.db.query(CourseUser).filter_by(email=user.email).all()
    courses: List[Course] = [course_user.course for course_user in course_users]
    return courses


def user_is_grader_in_course(user: User, course: Course) -> bool:
    # Returns true if the user is an instructor or CA in the course, false otherwise
    # This should be used for all local course operations
    # For *creating* the local course and syncing the roster with Autolab, use `user_is_grader_in_autolab_course`
    if user.is_admin:
        return True

    course_user: CourseUser = g.db.query(CourseUser).filter_by(email=user.email, course=course).first()
    if course_user is None:
        return False
    return course_user.is_grader()


def ensure_user_is_grader_in_course(user: User, course: Course):
    if not user_is_grader_in_course(user, course):
        abort(403, f"{user.email} is not an instructor or course assistant in {course.name}.")


def get_course_by_name_or_404(course_name: str) -> Course:
    course: Course = g.db.query(Course).filter_by(name=course_name).first()
    if course is None:
        abort(404, "Course not found.")
    return course


def get_course_user_by_email_or_404(course: Course, user_email: str) -> CourseUser:
    course_user: CourseUser = g.db.query(CourseUser).filter_by(email=user_email, course=course).first()
    if course_user is None:
        abort(404, f"User does not exist in course {course.name}.")
    return course_user


def sync_roster_from_autolab(course_name: str):
    # Sync the current local course roster with the one from Autolab
    logger.info(f"Syncing roster from Autolab for course {course_name}")

    local_course: Course = g.db.query(Course).filter_by(name=course_name).first()
    if local_course is None:
        abort(404, "Course not found. Please create it first.")

    if not user_is_grader_in_autolab_course(g.user.email, course_name):
        abort(403, "You are not an instructor or course assistant in this course on Autolab.")

    # Get the current roster from our local database
    existing_course_users: Sequence[CourseUser] = g.db.query(CourseUser).filter_by(course=local_course).all()
    existing_course_user_email_dict: Dict[str, CourseUser] = {
        course_user.email: course_user for course_user in existing_course_users
    }

    # Get the current roster from Autolab
    autolab = current_app.autolab
    autolab_course_users: List[dict] = autolab.course_users(course_name)["users"]
    autolab_course_user_email_dict: Dict[str, dict] = {
        autolab_course_user["email"]: autolab_course_user for autolab_course_user in autolab_course_users
    }

    # Delete users that exist locally but not in Autolab
    for course_user in existing_course_users:
        if course_user.email not in autolab_course_user_email_dict:
            logger.info(f"Deleted user {course_user.to_dict()} from course {course_name}")
            g.db.delete(course_user)

    # Create users that exist in Autolab but not locally
    new_user_email_set: Set[str] = set()
    autolab_course_user: dict
    for autolab_course_user in autolab_course_users:
        email: str = autolab_course_user["email"]
        if email not in existing_course_user_email_dict:
            display_name: str = autolab_course_user["display_name"]
            role: CourseRole = string_to_course_role(autolab_course_user["role"])
            course_user: CourseUser = CourseUser(email=email, display_name=display_name, role=role, course=local_course)
            g.db.add(course_user)
            new_user_email_set.add(email)
            logger.info(f"Created user {course_user.to_dict()} in course {course_name}")

    # Update users that exist in both Autolab and locally
    email: str
    course_user: dict
    for email, course_user in autolab_course_user_email_dict.items():
        if email not in new_user_email_set:
            display_name: str = course_user["display_name"]
            role: CourseRole = string_to_course_role(course_user["role"])
            course_user: CourseUser = existing_course_user_email_dict[email]
            if course_user.display_name != display_name or course_user.role != role:
                old_course_user: Dict[str, any] = course_user.to_dict()
                course_user.display_name = display_name
                course_user.role = role
                logger.info(
                    f"Updated user {email} in course {course_name} from "
                    f"{old_course_user} to {course_user.to_dict()}"
                )

    g.db.commit()


# Require login for all routes in this blueprint
@gat.before_request
def require_login():
    if g.user is None:
        abort(401)


@gat.route("/")
def index_view():
    return f"Hello from GAT (Grader Assignment Tool), {g.user.username}!"


@gat.route("/my-autolab-courses/", methods=["GET"])
def my_autolab_courses_view():
    courses = get_current_user_autolab_courses()
    return jsonify(courses)


@gat.route("/create-course/<course_name>/", methods=["POST"])
def create_course_view(course_name: str):
    # Given an Autolab course name, create a corresponding course in our database, if the user has permission
    in_course: bool
    course_info: Optional[dict]
    in_course, course_info = user_is_grader_in_autolab_course(g.user.email, course_name)
    if not in_course:
        abort(403, "You are not an instructor or course assistant in this course on Autolab.")

    # Check if the course already exists in our database
    course = g.db.query(Course).filter_by(name=course_name).first()
    if course is not None:
        abort(400, "This course has already been created.")

    display_name = f"{course_info['display_name']} ({course_info['semester']})"
    technical_name = course_info["name"]

    # Create the course in our database
    course = Course(name=technical_name, display_name=display_name, created_by_user=g.user)
    g.db.add(course)
    g.db.commit()

    sync_roster_from_autolab(course_name)

    return jsonify({
        "success": True,
        "data": course.to_dict()
    })


@gat.route("/my-courses/", methods=["GET"])
def my_courses_view():
    courses = get_grader_courses(g.user)
    return jsonify({
        "success": True,
        "data": [course.to_dict() for course in courses]
    })


@gat.route("/course/<course_name>/autolab-sync/", methods=["POST"])
def course_autolab_sync_view(course_name: str):
    # The `sync_roster_from_autolab` function handles permission checking and will raise an exception on failure
    sync_roster_from_autolab(course_name)
    return jsonify({
        "success": True
    })


@gat.route("/course/<course_name>/users/", methods=["GET"])
def course_users_view(course_name: str):
    # Returns a list of graders and students in the course, with the current user first (if they are a grader)
    course: Course = get_course_by_name_or_404(course_name)
    ensure_user_is_grader_in_course(g.user, course)

    course_users: Sequence[CourseUser] = \
        g.db.query(CourseUser).filter_by(course=course).order_by(CourseUser.email).all()
    graders: List[dict] = []
    students: List[dict] = []
    current_user_in_graders_roster: bool = False

    course_user: CourseUser
    for course_user in course_users:
        if course_user.is_grader():
            user_dict: dict = course_user.to_dict()
            if course_user.email == g.user.email:
                user_dict["is_current_user"] = True
                current_user_in_graders_roster = True
                graders.insert(0, user_dict)
            else:
                graders.append(user_dict)
        else:
            students.append(course_user.to_dict())

    ret = {
        "success": True,
        "data": {
            "course": course.to_dict(),
            "current_user_in_graders_roster": current_user_in_graders_roster,
            "graders": graders,
            "students": students
        }
    }

    return jsonify(ret)


@gat.route("/course/<course_name>/users/<user_email>/set-grader-hours/<int:hours>/", methods=["POST"])
def course_set_grader_hours_view(course_name: str, user_email: str, hours: int):
    # Set the number of hours a grader should work for a course
    course: Course = get_course_by_name_or_404(course_name)
    ensure_user_is_grader_in_course(g.user, course)

    course_user: CourseUser = get_course_user_by_email_or_404(course, user_email)

    # Check that the target user is a grader
    if not course_user.is_grader():
        abort(400, "Hours cannot be assigned to students.")

    # Check that the hours are reasonable
    if hours < 0:
        abort(400, "Hours must be non-negative.")
    elif hours > 1000:
        abort(400, "Hours must be at most 1000.")

    course_user.grading_hours = hours
    g.db.commit()

    logger.info(f"Set grader hours for {user_email} in course {course_name} to {hours}.")

    return jsonify({
        "success": True,
        "data": course_user.to_dict()
    })
