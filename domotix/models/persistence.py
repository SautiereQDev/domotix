"""
Modèles SQLAlchemy pour la persistance.

Ce module contient les modèles SQLAlchemy utilisés pour la persistance
des dispositifs dans la base de données.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Float, String

if TYPE_CHECKING:
    from domotix.core.database import Base
else:
    from domotix.core.database import Base


class DeviceModel(Base):  # type: ignore
    """Modèle SQLAlchemy pour tous les dispositifs."""

    __tablename__ = "devices"

    id = Column(String(36), primary_key=True)  # UUID en string
    name = Column(String(255), nullable=False)
    device_type = Column(String(50), nullable=False)
    location = Column(String(255), nullable=True)

    # Colonnes spécifiques selon le type
    is_on = Column(Boolean, nullable=True)  # Pour les lampes
    is_open = Column(Boolean, nullable=True)  # Pour les volets
    value = Column(Float, nullable=True)  # Pour les capteurs

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', type={self.device_type})>"
