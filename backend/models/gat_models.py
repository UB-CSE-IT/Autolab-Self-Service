import enum

from sqlalchemy import DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db import Base
from backend.models.user import User


class CourseRole(enum.Enum):
    INSTRUCTOR = "instructor"
    TA = "course_assistant"
    STUDENT = "student"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by_user: Mapped["User"] = relationship()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
        }


class CourseUser(Base):
    __tablename__ = "course_users"

    # Note that the "user" may not exist in our database, so we can only store their email address

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    course: Mapped["Course"] = relationship()
    email: Mapped[str] = mapped_column(nullable=False)
    display_name: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[CourseRole] = mapped_column(nullable=False)
    grading_hours: Mapped[int] = mapped_column(nullable=False, default=0)

    UniqueConstraint(course_id, email)

    def is_grader(self) -> bool:
        return self.role == CourseRole.INSTRUCTOR or self.role == CourseRole.TA

    def to_dict(self):
        ret = {
            "email": self.email,
            "display_name": self.display_name,
            "role": self.role.value,
            "is_grader": self.is_grader(),
        }
        if self.is_grader():
            ret["grading_hours"] = self.grading_hours

        return ret


class CourseConflictOfInterest(Base):
    __tablename__ = "course_conflicts_of_interest"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    course: Mapped["Course"] = relationship()
    grader_email: Mapped[str] = mapped_column(nullable=False)  # They may not exist as a user in our database
    student_email: Mapped[str] = mapped_column(nullable=False)

    UniqueConstraint(course_id, grader_email, student_email)

    def to_dict(self):
        return {
            "grader_email": self.grader_email,
            "student_email": self.student_email,
        }


class CourseGradingAssignment(Base):
    __tablename__ = "course_grading_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    course: Mapped["Course"] = relationship()
    assessment_name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by_user: Mapped["User"] = relationship()
    archived: Mapped[bool] = mapped_column(nullable=False, default=False)
    assessment_display_name: Mapped[str] = mapped_column(nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "course": self.course.to_dict(),
            "assessment_name": self.assessment_name,
            "created_at": self.created_at.isoformat(),
            "created_by_email": self.created_by_user.email,
            "created_by_display_name": self.created_by_user.display_name,
            "archived": self.archived,
            "assessment_display_name": self.assessment_display_name,
        }


class CourseGradingAssignmentPair(Base):
    __tablename__ = "course_grading_assignment_pairs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_grading_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("course_grading_assignments.id"),
        nullable=False)
    course_grading_assignment: Mapped["CourseGradingAssignment"] = relationship()
    grader_email: Mapped[str] = mapped_column(nullable=False)
    student_email: Mapped[str] = mapped_column(nullable=False)
    submission_url: Mapped[str] = mapped_column(nullable=False)
    completed: Mapped[bool] = mapped_column(nullable=False, default=False)
    submission_version: Mapped[int] = mapped_column(nullable=False, default=0)

    UniqueConstraint(course_grading_assignment_id, grader_email, student_email)

    def to_dict(self):
        # This is less verbose than most because it will be called many times to build a list
        return {
            "grader_email": self.grader_email,
            "student_email": self.student_email,
            "submission_url": self.submission_url,
            "completed": self.completed,
            "submission_version": self.submission_version,
        }
