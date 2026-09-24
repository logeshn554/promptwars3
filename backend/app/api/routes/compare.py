from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_comparison_service
from app.domain.schemas.document_schemas import ComparisonResult
from app.services.comparison_service import ComparisonService

router = APIRouter(prefix="/compare", tags=["Comparison"])

class CompareRequest(BaseModel):
    doc_a_id: UUID = Field(..., description="Document ID of base version (Version A)")
    doc_b_id: UUID = Field(..., description="Document ID of revised version (Version B)")

@router.post(
    "",
    response_model=ComparisonResult,
    summary="Compare two documents and detect semantic clause changes",
)
async def compare_documents(
    payload: CompareRequest,
    comparison_service: ComparisonService = Depends(get_comparison_service),
) -> ComparisonResult:
    return await comparison_service.compare_documents(
        doc_a_id=payload.doc_a_id,
        doc_b_id=payload.doc_b_id,
    )
