import datetime
import pytz
from typing import Tuple, Optional

from flask import g
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from backend.db import Base
from backend.models.user import User
from backend.utils import generate_random_string, sha256_hash


class Session(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    hashed_token = Column(String)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    logged_out_at = Column(DateTime(timezone=True), default=None)

    @staticmethod
    def create(user: User) -> Tuple["Session", str]:
        # Create a session for a user and return the session and the unhashed token
        assert isinstance(user, User), "Invalid user while creating session."
        token: str = generate_random_string(256)
        hashed_token: str = sha256_hash(token)
        s = Session(
            user_id=user.id,
            hashed_token=hashed_token,
            expires_at=datetime.datetime.now() + datetime.timedelta(days=15),
        )
        g.db.add(s)
        g.db.commit()
        return s, token

    def logout(self):
        # Set the logged_out_at field to the current time
        self.logged_out_at = func.now()
        g.db.commit()

    @staticmethod
    def get_session(unhashed_token) -> Optional["Session"]:
        hashed_token = sha256_hash(unhashed_token)
        session = g.db.query(Session).filter(Session.hashed_token == hashed_token).first()
        return session

    @staticmethod
    def get_user(unhashed_token) -> Optional[User]:
        # Given an unhashed token, return the user associated with the session if one exists
        session = Session.get_session(unhashed_token)
        if session is None or session.expires_at < datetime.datetime.now(pytz.utc) or session.logged_out_at is not None:
            return None
        return session.user

    def __repr__(self):
        return f"<Session {self.id} ({self.user.username})>"
