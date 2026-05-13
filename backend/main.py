import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from apis.authentication.router import router as authentication_router
from apis.members.router import router as members_router
from apis.trainers.router import router as trainers_router
from apis.membership_plans.router import router as membership_plans_router
from apis.sessions.router import router as sessions_router
from apis.workouts.router import router as workouts_router
from apis.attendance.router import router as attendance_router
from apis.payments.router import router as payments_router
from apis.equipments.router import router as equipments_router
from apis.etc.router import router as etc_router

# Initialize the FastAPI app with a title and version shown in Swagger docs
app = FastAPI(title="Gym Management System API", version="2.0")


@app.on_event("startup")
def startup():
    if os.getenv("DB_INIT_ON_STARTUP", "false").lower() == "true":
        init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication_router)
app.include_router(members_router)
app.include_router(trainers_router)
app.include_router(membership_plans_router)
app.include_router(sessions_router)
app.include_router(workouts_router)
app.include_router(attendance_router)
app.include_router(payments_router)
app.include_router(equipments_router)
app.include_router(etc_router)
