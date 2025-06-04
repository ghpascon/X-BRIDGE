from sqlalchemy import Column, Integer, String, DateTime
from app.db.session import Base

class DbTag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime)                   
    device = Column(String(50))             
    epc = Column(String(50))             
    tid = Column(String(50))
    ant = Column(Integer)
    rssi = Column(Integer)