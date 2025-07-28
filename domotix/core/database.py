# pylint: disable=import-error
#
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_database_url():
    """Retrieve the database URL."""
    domotix_db_path = os.getenv("DOMOTIX_DB_PATH")
    if domotix_db_path:
        return f"sqlite:///{domotix_db_path}"
    return os.getenv("DATABASE_URL", "sqlite:///./domotix.db")


# Initial configuration
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


"""Singleton class for database configuration"""


class DatabaseConfig:
    current_db_url = DATABASE_URL
    engine = engine
    session_local = SessionLocal


def reconfigure_database():
    """Reconfigure the database if the URL has changed."""
    new_url = get_database_url()
    if new_url != DatabaseConfig.current_db_url:
        DatabaseConfig.current_db_url = new_url
        DatabaseConfig.engine = create_engine(new_url)
        DatabaseConfig.session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=DatabaseConfig.engine
        )


def create_session():
    """Create a new database session."""
    reconfigure_database()
    return DatabaseConfig.session_local()


def create_tables():
    """Create all tables in the database."""
    reconfigure_database()

    Base.metadata.create_all(bind=DatabaseConfig.engine)
