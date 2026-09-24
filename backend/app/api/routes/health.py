from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(tags=["Health"])

class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    app_name: str
    environment: str
    llm_provider: str
    embedding_provider: str

@router.get("/health", response_model=HealthCheckResponse, summary="Service health check")
def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        llm_provider=settings.LLM_PROVIDER,
        embedding_provider=settings.EMBEDDING_PROVIDER,
    )
