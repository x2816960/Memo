from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.models import User, Task, Attachment, SystemConfig
from app.routers import auth, tasks, attachments, admin
from app.services.auth import init_admin_user
from app.utils.config import init_default_config
from app.database import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and init default data
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        init_admin_user(db)
        init_default_config(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="Memo API",
    description="Memo - Todo Task Management System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(attachments.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "Memo API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
