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


class CourseConflictOfInterest(Base):
    __tablename__ = "course_conflicts_of_interest"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    course: Mapped["Course"] = relationship()
    grader_email: Mapped[str] = mapped_column(nullable=False)  # They may not exist as a user in our database
    student_email: Mapped[str] = mapped_column(nullable=False)

    UniqueConstraint(course_id, grader_email, student_email)


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

    UniqueConstraint(course_grading_assignment_id, grader_email, student_email)
