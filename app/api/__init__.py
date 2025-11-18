from fastapi import APIRouter

from app.api.v1.docs import router as docs_router
from app.api.v1.topic import router as topic_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(topic_router)

__all__ = ["api_router", "docs_router"]
