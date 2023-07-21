import logging

from flask import g
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from backend.db import Base

logger = logging.getLogger("portal")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    person_number = Column(String, nullable=False, unique=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    sessions = relationship("Session", backref="user")
    registered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    login_count = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def create(username: str, first_name: str, last_name: str, person_number: str) -> "User":
        u = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            person_number=person_number,
        )
        g.db.add(u)
        g.db.commit()
        logger.info(f"Created new user {u.to_dict()}")
        return u

    def login(self):
        self.login_count += 1
        self.last_login = func.now()
        logger.info(f"User {self.username} logged in. This is their login number {self.login_count}")
        g.db.commit()

    def to_dict(self):
        return {
            "username": self.username,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "isAdmin": self.is_admin,
        }

    @property
    def email(self):
        return f"{self.username}@buffalo.edu"

    @staticmethod
    def get_by_username(username: str) -> "User":
        logger.debug(f"Getting user by username {username}")
        return g.db.query(User).filter(User.username == username).first()
