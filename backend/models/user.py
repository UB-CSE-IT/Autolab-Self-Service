from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from backend.db import Base, get_db_session


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    person_number = Column(String)
    is_admin = Column(Boolean, default=False)
    sessions = relationship("Session", backref="user")
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    login_count = Column(Integer, default=0)

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
        with get_db_session() as db:
            db.add(u)
            db.commit()
        return u

    def login(self):
        with get_db_session() as db:
            self.login_count += 1
            self.last_login = func.now()
            db.commit()

    def to_dict(self):
        return {
            "username": self.username,
            "firstName": self.first_name,
            "lastName": self.last_name,
        }

    @staticmethod
    def get_by_username(username: str) -> "User":
        return get_db_session().query(User).filter(User.username == username).first()
