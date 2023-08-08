from typing import List, Any, Dict

from backend.connections.course import Course


class Instructor:
    def __init__(self, username: str):
        self.username = username
        self.courses: List[Course] = []

    def add_course(self, course: Course):
        self.courses.append(course)

    def __repr__(self):
        return f"<Instructor {self.username} {self.courses}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "courses": [course.to_dict() for course in self.courses]
        }
