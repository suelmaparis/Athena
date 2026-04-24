from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # permite tudo (para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SOSRequest(BaseModel):
    latitude: float
    longitude: float

@app.post("/sos")
def receive_sos(data: SOSRequest):
    print(f"SOS recebido: {data.latitude}, {data.longitude}")
    return {"message": "SOS recebido com sucesso"}

alerts = []

@app.post("/sos")
def receive_sos(data: SOSRequest):
    alert = {
        "latitude": data.latitude,
        "longitude": data.longitude
    }
    alerts.append(alert)

    print(f"🚨 ALERTA: {alert}")

    return {"message": "SOS enviado com sucesso"}

@app.get("/alerts")
def get_alerts():
    return alerts