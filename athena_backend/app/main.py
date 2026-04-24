from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 1️⃣ MODELOS PRIMEIRO

class User(BaseModel):
    username: str

class SOSRequest(BaseModel):
    latitude: float
    longitude: float
    username: str

# 🔥 2️⃣ VARIÁVEIS

users = []
alerts = []

# 🔥 3️⃣ ROTAS DEPOIS

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

    print(f"🚨 ALERTA de {data.username}: {alert}")

    return {"message": "SOS enviado com sucesso"}

@app.get("/alerts")
def get_alerts():
    return alerts