from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
from passlib.context import CryptContext
from app.database import engine, Base, SessionLocal
from app.models import UserDB


Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password[:72])

def verify_password(plain, hashed):
    return pwd_context.verify(plain[:72], hashed)


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
    password: str

class SOSRequest(BaseModel):
    latitude: float
    longitude: float
    username: str
# 🔥 ROTAS

@app.post("/register")
def register(user: User):
    db = SessionLocal()

    existing_user = db.query(UserDB).filter(UserDB.username == user.username).first()

    if existing_user:
        db.close()
        return {"message": "User already exists"}

    new_user = UserDB(
        username=user.username,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.close()

    return {"message": "User created successfully"}


@app.post("/login")
def login(user: User):
    db = SessionLocal()

    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()

    if not db_user:
        db.close()
        return {"message": "User not found"}

    if not verify_password(user.password, db_user.password):
        db.close()
        return {"message": "Wrong password"}

    db.close()
    return {"message": "Login successful"}

@app.post("/sos")
def receive_sos(data: SOSRequest):
    db = SessionLocal()

    db_user = db.query(UserDB).filter(UserDB.username == data.username).first()

    if not db_user:
        db.close()
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

