from sqlalchemy import Column, DateTime, Integer, String, Boolean

from app.db.session import Base


class DbTag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    timestamp  = Column(DateTime)
    device = Column(String(50))
    epc = Column(String(50))
    tid = Column(String(50))
    ant = Column(Integer)
    rssi = Column(Integer)


class DbEvent(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp  = Column(DateTime)
    device = Column(String(50))
    event_type = Column(String(50))
    event_data = Column(String(200))
