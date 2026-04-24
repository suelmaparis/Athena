from fastapi import APIRouter
from app.models import Incident

router = APIRouter()

incidents = []

@router.get("/")
def root():
    return {"message": "Athena API running"}

@router.post("/sos")
def send_sos(incident: Incident):
    incidents.append(incident)
    return {
        "status": "SOS received",
        "total_alerts": len(incidents)
    }

@router.get("/incidents")
def get_incidents():
    return incidents
