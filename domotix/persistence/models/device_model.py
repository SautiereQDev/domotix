from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.sql import func

from domotix.globals import DeviceState, DeviceType
from domotix.persistence.database import Base


class DeviceModel(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    device_type: Column[DeviceType] = Column(Enum(DeviceType), nullable=False)
    current_state: Column[DeviceState] = Column(Enum(DeviceState), nullable=False)
    created_at: Column[DateTime] = Column(DateTime(), server_default=func.now())
    updated_at: Column[DateTime] = Column(DateTime(), onupdate=func.now())
