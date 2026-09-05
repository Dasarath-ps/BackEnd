from app.routers.auth import router as auth_router
from app.routers.colleges import router as colleges_router
from app.routers.students import router as students_router

__all__ = ["auth_router", "colleges_router", "students_router"]
