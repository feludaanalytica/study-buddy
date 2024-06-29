from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from study_buddy.utilities.dbengine import db_engine


Base = declarative_base()


class User(Base):
    """User data model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


Base.metadata.create_all(db_engine)  # Create tables
