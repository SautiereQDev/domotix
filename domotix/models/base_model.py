"""
SQLAlchemy models for persistence.

This module contains the SQLAlchemy models used for device persistence
in the database.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Float, String

if TYPE_CHECKING:
    from domotix.core.database import Base
else:
    from domotix.core.database import Base


class DeviceModel(Base):  # type: ignore
    """SQLAlchemy model for all devices."""

    __tablename__ = "devices"

    id = Column(String(36), primary_key=True)  # UUID as string
    name = Column(String(255), nullable=False)
    device_type = Column(String(50), nullable=False)
    location = Column(String(255), nullable=True)

    # Specific columns depending on the type
    is_on = Column(Boolean, nullable=True)  # For lamps
    is_open = Column(Boolean, nullable=True)  # For shutters
    value = Column(Float, nullable=True)  # For sensors

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', type={self.device_type})>"
