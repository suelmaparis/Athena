from pydantic import BaseModel
from datetime import datetime

class Incident(BaseModel):
    user: str
    latitude: float
    longitude: float
    description: str
    timestamp: datetime = datetime.utcnow()
