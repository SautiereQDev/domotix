# pylint: disable=import-error
#
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./domotix.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_session():
    """Crée une nouvelle session de base de données."""
    return SessionLocal()


def create_tables():
    """Crée toutes les tables dans la base de données."""
    # Import pour déclencher la création des modèles
    from domotix.models.persistence import DeviceModel  # noqa: F401

    Base.metadata.create_all(bind=engine)
