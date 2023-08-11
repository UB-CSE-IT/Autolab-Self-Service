import logging

import cachetools.func
from typing import Tuple, Optional, List, Sequence, Set, Dict

from flask import abort, current_app, jsonify
from flask import Blueprint, g

from backend.connections.autolab_api_connection import AutolabApiConnection
from backend.models.gat_models import Course, CourseUser, CourseConflictOfInterest, CourseGradingAssignment, \
    CourseGradingAssignmentPair, CourseRole
from backend.models.user import User

logger = logging.getLogger("portal")

gat = Blueprint("gat", __name__)


def get_current_user_autolab_courses() -> dict:
    email_address = g.user.email
    autolab: AutolabApiConnection = current_app.autolab
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
    autolab: AutolabApiConnection = current_app.autolab
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


def ensure_current_user_is_grader_in_autolab_course(course_name):
    if g.user.is_admin:
        return
    if not user_is_grader_in_autolab_course(g.user.email, course_name):
        abort(403, "You are not an instructor or course assistant in this course on Autolab.")


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

    ensure_current_user_is_grader_in_autolab_course(course_name)

    # Get the current roster from our local database
    existing_course_users: Sequence[CourseUser] = g.db.query(CourseUser).filter_by(course=local_course).all()
    existing_course_user_email_dict: Dict[str, CourseUser] = {
        course_user.email: course_user for course_user in existing_course_users
    }

    # Get the current roster from Autolab
    autolab: AutolabApiConnection = current_app.autolab
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


def create_grading_assignments(
        graders: Dict[str, Dict[str, any]],
        conflicts_of_interest: List[Dict[str, str]],
        submissions: Dict[str, Dict[str, any]]
) -> Dict[str, Dict[str, any]]:
    # Create a grader to student one-to-many mapping accounting for the grader's
    # number of hours and avoiding conflicts of interest
    #
    # `graders` should be formatted like: Dict of (grader email address) -> CourseUser.to_dict()
    #   {
    #     "grader@buffalo": {
    #       "display_name": "First Last",
    #       "email": "grader@buffalo.edu",
    #       "grading_hours": 10,
    #       "is_grader": True,
    #       "role": "course_assistant"
    #     }, ...
    #   }
    #
    # `conflicts_of_interest` should be formatted like: List of CourseConflictOfInterest.to_dict()
    #   [
    #     {
    #       "grader_email": "grader@buffalo",
    #       "student_email": "student@buffalo"
    #     }, ...
    #   ]
    #
    # `submissions` should be formatted like: Dict of (student email address) -> Submission dict
    #   {
    #     "student@buffalo": {
    #       "email": "student@buffalo.edu",
    #       "display_name": "First Last"
    #       "version": 22
    #       "url": "https://autolab.cse.buffalo.edu/courses/cse-it-test-course/assessments/pdftest/submissions/22/view",
    #     }, ...
    #   }
    #
    # Returns a dictionary mapping grader email to a list of submissions to grade, like:
    #   {
    #     "grader@buffalo": [
    #       {
    #         "email": "student1@buffalo",
    #         "display_name": "First Last",
    #         "version": 22,
    #         "url": "https://autolab.cse.buffalo.edu/courses/.../pdftest/submissions/22/view",
    #       }, ...
    #     ], ...
    #   }

    # TODO implement the algorithm

    # TODO this isn't actually what will be returned
    ret = {
        "graders": graders,
        "conflicts_of_interest": conflicts_of_interest,
        "submissions": submissions,
    }

    return ret


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


@gat.route("/course/<course_name>/users/<grader_email>/conflict-of-interest/<student_email>/", methods=["POST"])
def course_create_conflict_of_interest_view(course_name: str, grader_email: str, student_email: str):
    # Create a conflict of interest between a grader and a student
    course: Course = get_course_by_name_or_404(course_name)
    ensure_user_is_grader_in_course(g.user, course)

    grader: CourseUser = get_course_user_by_email_or_404(course, grader_email)
    student: CourseUser = get_course_user_by_email_or_404(course, student_email)

    # Check that the target grader is a grader
    if not grader.is_grader():
        abort(400, "Conflicts of interest cannot be assigned to students.")

    # Check that the target student is a student
    if student.is_grader():
        abort(400, "A grader cannot have a conflict of interest with another grader.")
        # This also prevents a grader from having a conflict of interest with themselves

    # Check that the conflict of interest does not already exist
    conflict_of_interest: CourseConflictOfInterest = \
        g.db.query(CourseConflictOfInterest).filter_by(
            course=course, grader_email=grader.email, student_email=student.email).first()
    if conflict_of_interest is not None:
        abort(400, "This conflict of interest already exists.")

    # Create the conflict of interest
    conflict_of_interest = CourseConflictOfInterest(course=course,
                                                    grader_email=grader.email,
                                                    student_email=student.email)
    g.db.add(conflict_of_interest)
    g.db.commit()

    logger.info(f"Created conflict of interest between {grader_email} and {student_email} in course {course_name}.")

    return jsonify({
        "success": True,
        "data": conflict_of_interest.to_dict()
    })


@gat.route("/course/<course_name>/users/<grader_email>/conflict-of-interest/<student_email>/", methods=["DELETE"])
def course_delete_conflict_of_interest_view(course_name: str, grader_email: str, student_email: str):
    # Delete a conflict of interest between a grader and a student
    course: Course = get_course_by_name_or_404(course_name)
    ensure_user_is_grader_in_course(g.user, course)

    # Check that the conflict of interest exists
    conflict_of_interest: CourseConflictOfInterest = \
        g.db.query(CourseConflictOfInterest).filter_by(
            course=course, grader_email=grader_email, student_email=student_email).first()
    if conflict_of_interest is None:
        abort(400, "This conflict of interest does not exist.")

    conflict_dict: dict = conflict_of_interest.to_dict()

    # Delete the conflict of interest
    g.db.delete(conflict_of_interest)
    g.db.commit()

    logger.info(f"Deleted conflict of interest between {grader_email} and {student_email} in course {course_name}.")

    return jsonify({
        "success": True,
        "data": conflict_dict
    })


@gat.route("/course/<course_name>/users/<user_email>/", methods=["GET"])
def course_user_view(course_name: str, user_email: str):
    # Get a user in a course
    course: Course = get_course_by_name_or_404(course_name)
    ensure_user_is_grader_in_course(g.user, course)

    course_user: CourseUser = get_course_user_by_email_or_404(course, user_email)

    if course_user.is_grader():
        conflicts_of_interest: Sequence[CourseConflictOfInterest] = g.db.query(CourseConflictOfInterest) \
            .filter_by(course=course, grader_email=user_email).all()
        conflicts_of_interest_emails = [conflict.student_email for conflict in conflicts_of_interest]
    else:
        conflicts_of_interest: Sequence[CourseConflictOfInterest] = g.db.query(CourseConflictOfInterest) \
            .filter_by(course=course, student_email=user_email).all()
        conflicts_of_interest_emails = [conflict.grader_email for conflict in conflicts_of_interest]

    data = {
        "course": course.to_dict(),
        "user": course_user.to_dict(),
        "conflicts_of_interest": conflicts_of_interest_emails
    }

    return jsonify({
        "success": True,
        "data": data
    })


@gat.route("/course/<course_name>/autolab-assessments/", methods=["GET"])
def course_autolab_assessments_view(course_name: str):
    # Get all Autolab assessments in a course. Requires being a grader in the course locally and on Autolab.
    course: Course = get_course_by_name_or_404(course_name)
    ensure_user_is_grader_in_course(g.user, course)
    ensure_current_user_is_grader_in_autolab_course(course_name)

    autolab: AutolabApiConnection = current_app.autolab
    assessments = autolab.course_assessments(course_name)["assessments"]

    data = {
        "course": course.to_dict(),
        "assessments": assessments
    }

    return jsonify({
        "success": True,
        "data": data
    })


@gat.route("/course/<course_name>/create-grading-assignment/<assessment_name>/", methods=["POST"])
def course_create_grading_assignment_view(course_name: str, assessment_name: str):
    # Create a new grading assignment for an Autolab assessment in a course. Requires being a grader in the course.
    # Maps graders to students who submitted the assessment accounting for conflicts of interest and grading hours.

    # Permission checks
    course: Course = get_course_by_name_or_404(course_name)
    ensure_user_is_grader_in_course(g.user, course)
    ensure_current_user_is_grader_in_autolab_course(course_name)

    # Get the assessment data from Autolab
    autolab: AutolabApiConnection = current_app.autolab
    assessment: dict = autolab.get_assessment_submissions(course_name, assessment_name)
    submissions_by_student: dict = {submission["email"]: submission for submission in assessment["submissions"]}

    # Get the conflicts of interest
    course_conflicts_of_interest: Sequence[CourseConflictOfInterest] = \
        g.db.query(CourseConflictOfInterest).filter_by(course=course).all()
    conflicts_of_interest_list: List[Dict[str, any]] = [conflict.to_dict() for conflict in course_conflicts_of_interest]

    # Get the graders in the course
    course_users: Sequence[CourseUser] = g.db.query(CourseUser).filter_by(course=course).all()
    graders: Dict[str, Dict[str, any]] = {user.email: user.to_dict() for user in course_users if user.is_grader()}

    algo_response = create_grading_assignments(graders, conflicts_of_interest_list, submissions_by_student)

    # TODO Store the grading assignment in the database

    # TODO this isn't really all gonna be returned, just for testing
    ret = {
        "algo_response": algo_response,
        "course": course.to_dict(),
        "assessment": {
            "name": assessment["assessment_name"],
            "display_name": assessment["assessment_display_name"],
        },
        "submissions": submissions_by_student,
        "course_conflicts_of_interest": [conflict.to_dict() for conflict in course_conflicts_of_interest],
        "course_users": [user.to_dict() for user in course_users]
    }

    return jsonify({
        "success": True,
        "data": ret
    })
