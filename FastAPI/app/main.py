from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.models.course import Course, CourseMode
from app.routers import auth_router, colleges_router, students_router


def seed_default_courses():
    """Seeds default training courses specified in NurseBridge requirements."""
    db = SessionLocal()
    try:
        if db.query(Course).count() == 0:
            default_courses = [
                Course(
                    title="German Language (A1-B2)",
                    description="Comprehensive medical German training for nursing placement in Germany.",
                    mode=CourseMode.OFFLINE,
                    language="German",
                    level="B1",
                ),
                Course(
                    title="Professional Nursing Communication",
                    description="Clinical communication, patient rapport, and bedside documentation.",
                    mode=CourseMode.ONLINE,
                    language="English",
                    level="Professional",
                ),
                Course(
                    title="ICU & Emergency Critical Care Upskilling",
                    description="Advanced preparation for intensive care unit protocols and patient monitoring.",
                    mode=CourseMode.OFFLINE,
                    language="English",
                    level="Advanced",
                ),
            ]
            db.add_all(default_courses)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if not exist
    Base.metadata.create_all(bind=engine)
    seed_default_courses()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="NurseBridge nursing training + career + recruitment unified platform API.",
    lifespan=lifespan,
)

# Enable CORS for future React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular API routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(colleges_router, prefix=settings.API_V1_STR)
app.include_router(students_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "project": "NurseBridge Platform",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }
