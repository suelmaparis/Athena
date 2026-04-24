from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 ZONAS DE PERIGO
danger_zones = [
    {"name": "Zona Perigosa 1", "lat": 40.7128, "lon": -74.0060, "radius": 0.01},
]

def is_in_danger_zone(lat, lon):
    for zone in danger_zones:
        distance = math.sqrt((lat - zone["lat"])**2 + (lon - zone["lon"])**2)
        if distance < zone["radius"]:
            return zone["name"]
    return None

# 🔥 MODELOS
class User(BaseModel):
    username: str

class SOSRequest(BaseModel):
    latitude: float
    longitude: float
    username: str

# 🔥 VARIÁVEIS
users = []
alerts = []
received_alerts = []

# 🔥 ROTAS

@app.post("/register")
def register(user: User):
    users.append(user)
    return {"message": "User created"}

@app.post("/sos")
def receive_sos(data: SOSRequest):
    alert = {
        "user": data.username,
        "latitude": data.latitude,
        "longitude": data.longitude
    }

    alerts.append(alert)

    # 🔥 verificar zona de perigo
    zone = is_in_danger_zone(data.latitude, data.longitude)

    if zone:
        received_alerts.append({
            "from": "SYSTEM",
            "message": f"⚠️ Você entrou em {zone}",
            "latitude": data.latitude,
            "longitude": data.longitude
        })

    # 🔥 alerta normal
    received_alerts.append({
        "from": data.username,
        "message": "🚨 Alerta de emergência",
        "latitude": data.latitude,
        "longitude": data.longitude
    })

    print(f"🚨 ALERTA de {data.username}")

    return {"message": "SOS enviado"}

@app.get("/alerts")
def get_alerts():
    return alerts

@app.get("/received")
def get_received():
    return received_alerts