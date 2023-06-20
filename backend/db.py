import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

load_dotenv()

postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_db = os.getenv("POSTGRES_DB")
DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

engine = create_engine(DATABASE_URL)
get_db_session = scoped_session(
    sessionmaker(bind=engine, expire_on_commit=False))  # Use this in other files to get a session
Base = declarative_base()


def initialize():
    from backend.models.user import User  # Needed to create tables
    from backend.models.session import Session  # Needed to create tables
    Base.metadata.create_all(bind=engine)
