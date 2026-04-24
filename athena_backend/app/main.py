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
# 🔥 VARIÁVEIS
users = []
alerts = []
received_alerts = []

def is_in_danger_zone(lat, lon):
    for zone in danger_zones:
        distance = math.sqrt((lat - zone["lat"])**2 + (lon - zone["lon"])**2)
        if distance < zone["radius"]:
            return zone["name"]
    return None

# Models
class User(BaseModel):
    username: str

class SOSRequest(BaseModel):
    latitude: float
    longitude: float
    username: str
# 🔥 ROTAS

@app.post("/register")
def register(user: User):
    for u in users:
        if u.username == user.username:
            return {"message": "User already exists"}

    users.append(user)
    return {"message": "User created"}

@app.post("/login")
def login(user: User):
    for u in users:
        if u.username == user.username:
            return {"message": "Login successful"}

    return {"message": "User not found"}

@app.post("/sos")
def receive_sos(data: SOSRequest):

    # 🔐 validar usuário
    if not any(u.username == data.username for u in users):
        return {"message": "User not authenticated"}

    alert = {
        "user": data.username,
        "latitude": data.latitude,
        "longitude": data.longitude
    }

    alerts.append(alert.copy())

    zone = is_in_danger_zone(data.latitude, data.longitude)

    if zone:
        received_alerts.append({
            "from": "SYSTEM",
            "message": f"⚠️ You entered {zone}",
            "latitude": data.latitude,
            "longitude": data.longitude
        })

    received_alerts.append({
        "from": data.username,
        "message": "🚨 Emergency alert",
        "latitude": data.latitude,
        "longitude": data.longitude
    })

    return {"message": "SOS sent successfully"}

@app.get("/alerts")
def get_alerts():
    return alerts

@app.get("/received")
def get_received():
    return received_alerts

