from fastapi import APIRouter

from app.api.routes import compare, documents, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(documents.router)
api_router.include_router(compare.router)
