from typing import List, Dict, Optional, Any


class Course:
    def __init__(self, subject_source_key: str, course_number: str, course: str, course_type: str, term: str,
                 combined_section_id: str, term_source_key: str, course_id: str, class_number: str,
                 instructor: str):
        self.subject_source_key = subject_source_key
        self.course_number = course_number
        self.course = course
        self.course_type = course_type
        self.term = term
        self.combined_section_id = combined_section_id
        self.term_source_key = term_source_key
        self.course_id = course_id
        self.class_number = class_number
        self.instructor = instructor

        self.friendly_name = f"{self.subject_source_key} {self.course_number}"

    def __repr__(self):
        return f"<Course '{self.friendly_name}' {self.subject_source_key} {self.course_number} {self.course}" \
               f"{self.course_type} {self.term} '{self.suggested_name=}' " \
               f"{self.combined_section_id} {self.term_source_key} {self.course_id} " \
               f"{self.class_number} {self.instructor} (Unique ID: '{self.unique_identifier}', Crosslisted ID: " \
               f"{self.crosslisted_identifier})>"

    def __str__(self):
        return f"'{self.technical_name}' '{self.friendly_name}' taught by {self.instructor}"

    @property
    def unique_identifier(self) -> str:
        # Used to verify course information on backend when the instructor chooses a course
        return f"{self.term_source_key} {self.course_id} {self.class_number}"

    @property
    def crosslisted_identifier(self) -> Optional[str]:
        # This will be the same across two (or more) crosslisted courses
        if self.combined_section_id is None:
            return None
        return f"{self.term_source_key} {self.combined_section_id}"

    @property
    def semester_code(self) -> str:
        # Returns something like "f23" or "u24" based on the full "Fall 2023" or "Summer 2024" term
        term = self.term.lower()
        letter = term[0]
        if letter == "s" and term[1] == "u":
            # Account for summer
            letter = "u"
        return f"{letter}{term[-2:]}"

    @property
    def technical_name(self) -> str:
        # Used for URLs, less unique than unique_identifier
        return f"{self.subject_source_key.lower()}{self.course_number}-{self.semester_code}"

    @property
    def suggested_name(self):
        # A suggested display name for the course, but instructors can change it
        return f"{self.friendly_name}: {self.course}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subjectSourceKey": self.subject_source_key,
            "courseNumber": self.course_number,
            "course": self.course,
            "courseType": self.course_type,
            "term": self.term,
            "combinedSectionId": self.combined_section_id,
            "termSourceKey": self.term_source_key,
            "course_id": self.course_id,
            "class_number": self.class_number,
            "instructor": self.instructor,
            "friendlyName": self.friendly_name,
            "uniqueIdentifier": self.unique_identifier,
            "crosslistedIdentifier": self.crosslisted_identifier,
            "semesterCode": self.semester_code,
            "technicalName": self.technical_name,
            "suggestedName": self.suggested_name
        }
