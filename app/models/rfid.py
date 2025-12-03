from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db.session import Base
from .helpers import BaseModelMixin

class DbTag(Base, BaseModelMixin):
    """
    Database model for RFID tag readings.

    Stores information about RFID tags detected by readers including
    EPC, TID, antenna information, signal strength, and GTIN data.
    Devices can be indexed for better query performance.
    """

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=True, default=func.now())
    device = Column(String(50), nullable=False, index=True)
    epc = Column(String(24), nullable=False, index=True)
    tid = Column(String(24), nullable=True)
    ant = Column(Integer, nullable=True, default=1)
    rssi = Column(Integer, nullable=True)
    gtin = Column(String(24), nullable=True, index=True)


class DbEvent(Base, BaseModelMixin):
    """
    Database model for system events and logs.

    Stores various system events like device connections, errors,
    configuration changes, and other operational events.
    All fields are required (none can be null).
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    device = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(String(200), nullable=False)

