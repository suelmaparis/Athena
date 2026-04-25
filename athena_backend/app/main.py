import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
from passlib.context import CryptContext
from app.database import engine, Base, SessionLocal
from app.models import UserDB, AlertDB, DangerZoneDB
from fastapi import WebSocket
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

Base.metadata.create_all(bind=engine)

app = FastAPI()
connections = []
device_tokens = []

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password[:72])

def verify_password(plain, hashed):
    return pwd_context.verify(plain[:72], hashed)


def send_push_notification(title, body):
    for token in device_tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        messaging.send(message)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class SOSRequest(BaseModel):
    latitude: float
    longitude: float
    username: str
class User(BaseModel):
    username: str
    password: str

def is_in_danger_zone(db, lat, lon):
    zones = db.query(DangerZoneDB).all()

    for zone in zones:
        distance = math.sqrt(
            (lat - zone.latitude) ** 2 +
            (lon - zone.longitude) ** 2
        )

        if distance < zone.radius:
            return zone.name

    return None

def check_danger_zone(db, lat, lon):
    alerts = db.query(AlertDB).all()

    count = 0

    for alert in alerts:
        distance = math.sqrt(
            (lat - alert.latitude) ** 2 +
            (lon - alert.longitude) ** 2
        )

        if distance < 0.01:  # raio
            count += 1

    return count


# 🔥 ROTAS
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()  # mantém conexão viva
    except:
        connections.remove(websocket)

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
async def receive_sos(data: SOSRequest):
    db = SessionLocal()

    db_user = db.query(UserDB).filter(UserDB.username == data.username).first()

    if not db_user:
        db.close()
        return {"message": "User not authenticated"}

    new_alert = AlertDB(
        username=data.username,
        latitude=data.latitude,
        longitude=data.longitude
    )

    db.add(new_alert)
    db.commit()

    # 🔥 zonas inteligentes
    count = check_danger_zone(db, data.latitude, data.longitude)

    if count >= 3:
        existing_zone = db.query(DangerZoneDB).filter(
            DangerZoneDB.latitude == data.latitude,
            DangerZoneDB.longitude == data.longitude
        ).first()

        if not existing_zone:
            db.add(DangerZoneDB(
                name="High Risk Area",
                latitude=data.latitude,
                longitude=data.longitude,
                radius=0.01
            ))
            db.commit()

    # 🔥 WEBSOCKET
    for connection in connections:
        await connection.send_text(json.dumps({
            "type": "alert",
            "user": data.username,
            "latitude": data.latitude,
            "longitude": data.longitude
        }))

    # 🔥 PUSH (AGORA FUNCIONA)
    send_push_notification(
        "🚨 Emergency Alert",
        f"{data.username} sent an SOS"
    )

    db.close()
    return {"message": "SOS sent successfully"}

@app.get("/alerts")
def get_alerts():
    db = SessionLocal()

    alerts = db.query(AlertDB).all()

    result = []
    for a in alerts:
        result.append({
            "user": a.username,
            "latitude": a.latitude,
            "longitude": a.longitude
        })

    db.close()
    return result

@app.get("/create-zone")
def create_zone():
    db = SessionLocal()

    zone = DangerZoneDB(
        name="Danger Zone NYC",
        latitude=40.7128,
        longitude=-74.0060,
        radius=0.01
    )

    db.add(zone)
    db.commit()
    db.close()

    return {"message": "Zone created"}

@app.get("/zones")
def get_zones():
    db = SessionLocal()

    zones = db.query(DangerZoneDB).all()

    result = []
    for z in zones:
        result.append({
            "name": z.name,
            "latitude": z.latitude,
            "longitude": z.longitude,
            "radius": z.radius
        })

    db.close()
    return result

@app.post("/save-token")
def save_token(data: dict):
    device_tokens.append(data["token"])
    return {"message": "Token saved"}