from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


# 🚨 ALERTS
class AlertDB(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)


# ⚠️ DANGER ZONES
class DangerZoneDB(Base):
    __tablename__ = "danger_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float)