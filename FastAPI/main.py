"""
NurseBridge API Runner
Delegates application instance from app.main for uvicorn compatibility.
"""
from app.main import app

__all__ = ["app"]