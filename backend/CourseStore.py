import logging
from datetime import datetime, timedelta
from threading import Lock
from typing import List, Dict

from backend.connections.Course import Course
from backend.connections.InfosourceConnection import InfoSourceConnection
from backend.connections.Instructor import Instructor

logger = logging.getLogger("portal")


class CourseStore:

    def __init__(self, infosource: InfoSourceConnection):
        self.infosource = infosource
        self.cache_ttl = 600  # 10 minutes
        self.last_updated = datetime.now() - timedelta(seconds=self.cache_ttl + 1)
        self.courses_cache: List[Course] = []
        self.instructors_cache: Dict[str, Instructor] = {}  # username -> Instructor
        self.updating_lock = Lock()

    def update_from_database(self):
        logger.info("Updating course store from InfoSource database")
        courses: List[Course] = self.infosource.query_all_courses()

        crosslisted_courses: Dict[str, List[Course]] = {}  # crosslisted_identifier -> List[Course]

        for course in courses:
            # Get crosslisted courses
            if course.combined_section_id is not None:
                if course.crosslisted_identifier not in crosslisted_courses:
                    crosslisted_courses[course.crosslisted_identifier] = []
                crosslisted_courses[course.crosslisted_identifier].append(course)

        k: str
        v: List[Course]
        for k, v in crosslisted_courses.items():
            # Reduce crosslisted courses to a single course
            names: List[str] = []
            minimum_course: str = v[0].friendly_name
            for course in v:
                # Get all names of this course
                names.append(course.friendly_name)
                if course.friendly_name < minimum_course:
                    minimum_course = course.friendly_name
            for course in v:
                # Remove all but the minimum name of this course
                if course.friendly_name != minimum_course:
                    courses.remove(course)
            for course in v:
                # Combine all names of this course separated by / alphabetically
                names.sort()
                course.friendly_name = "/".join(names)

        professors: Dict[str, Instructor] = {}
        for course in courses:
            # Create professors and assign courses to them
            professor_username: str = course.instructor
            if professor_username not in professors:
                professors[professor_username] = Instructor(professor_username)
            professor: Instructor = professors[professor_username]
            professor.add_course(course)

        self.courses_cache = courses
        self.instructors_cache = professors

    def update_if_necessary(self):
        # Update from database if cache is stale, waits until data is available if called while updating
        with self.updating_lock:
            if (datetime.now() - self.last_updated).total_seconds() > self.cache_ttl:
                self.update_from_database()
                self.last_updated = datetime.now()

    def get_courses(self) -> List[Course]:
        logger.debug("Getting courses")
        # Get courses, read from local cache if fresh enough
        self.update_if_necessary()
        return self.courses_cache

    def get_professors(self) -> Dict[str, Instructor]:
        logger.debug("Getting professors")
        # Get professors, read from local cache if fresh enough
        self.update_if_necessary()
        return self.instructors_cache

    def get_by_unique_identifier(self, unique_id: str):
        logger.debug(f"Getting course by unique identifier {unique_id}")
        # Get course by unique identifier, read from local cache if fresh enough
        self.update_if_necessary()
        for course in self.courses_cache:
            if course.unique_identifier == unique_id:
                return course
        return None
