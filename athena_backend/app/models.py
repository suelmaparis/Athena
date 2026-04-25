from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String
from app.database import Base

class Incident(BaseModel):
    user: str
    latitude: float
    longitude: float
    description: str
    timestamp: datetime = datetime.utcnow()


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)