from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine
from app.routers import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if not exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="NurseBridge Platform API - Authentication & Multi-Portal Registration Service.",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication & Registration Router
app.include_router(auth_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "project": "NurseBridge Platform",
        "version": "1.0.0",
        "service": "Authentication & Registration",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }
