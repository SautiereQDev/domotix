# pylint: disable=import-error
#
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_database_url():
    """Récupère l'URL de la base de données."""
    domotix_db_path = os.getenv("DOMOTIX_DB_PATH")
    if domotix_db_path:
        return f"sqlite:///{domotix_db_path}"
    return os.getenv("DATABASE_URL", "sqlite:///./domotix.db")


# Configuration initiale
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Variables globales pour la reconfiguration
_current_db_url = DATABASE_URL
_engine = engine
_session_local = SessionLocal


def reconfigure_database():
    """Reconfigure la base de données si l'URL a changé."""
    global _current_db_url, _engine, _session_local, engine, SessionLocal

    new_url = get_database_url()
    if new_url != _current_db_url:
        _current_db_url = new_url
        _engine = create_engine(new_url)
        _session_local = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        engine = _engine
        SessionLocal = _session_local


def create_session():
    """Crée une nouvelle session de base de données."""
    reconfigure_database()
    return SessionLocal()


def create_tables():
    """Crée toutes les tables dans la base de données."""
    reconfigure_database()

    # Import pour déclencher la création des modèles
    from domotix.models.base_model import DeviceModel  # noqa: F401

    Base.metadata.create_all(bind=engine)
