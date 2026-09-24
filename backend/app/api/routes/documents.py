from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies import (
    get_checklist_service,
    get_document_service,
    get_lawyer_prep_service,
    get_qa_service,
)
from app.core.exceptions import DocumentNotFoundError
from app.domain.schemas.document_schemas import (
    ChecklistItem,
    ClauseAnalysis,
    DocumentMetadata,
    DocumentSummary,
    LawyerQuestionItem,
    LegalDocumentGraph,
    QARequest,
    QAResponse,
    StructuredObligation,
)
from app.repositories.document_store import document_store
from app.services.checklist_service import ChecklistService
from app.services.document_service import DocumentService
from app.services.lawyer_prep_service import LawyerPreparationService
from app.services.qa_service import QAService

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post(
    "",
    response_model=DocumentMetadata,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a legal document (PDF, DOCX, TXT)",
)
async def upload_document(
    file: UploadFile = File(...),
    doc_service: DocumentService = Depends(get_document_service),
) -> DocumentMetadata:
    return await doc_service.upload_and_process_document(file)

@router.get(
    "",
    response_model=list[DocumentMetadata],
    summary="List all uploaded documents",
)
def list_documents(
    doc_service: DocumentService = Depends(get_document_service),
) -> list[DocumentMetadata]:
    return doc_service.list_documents()

@router.get(
    "/{document_id}",
    response_model=DocumentMetadata,
    summary="Get document metadata",
)
def get_document(
    document_id: UUID,
    doc_service: DocumentService = Depends(get_document_service),
) -> DocumentMetadata:
    return doc_service.get_document_metadata(document_id)

@router.get(
    "/{document_id}/clauses",
    response_model=list[ClauseAnalysis],
    summary="Retrieve structured clauses and attention flags",
)
def get_clauses(document_id: UUID) -> list[ClauseAnalysis]:
    if not document_store.get_metadata(document_id):
        raise DocumentNotFoundError(f"Document {document_id} was not found.")
    return document_store.get_clauses(document_id)

@router.get(
    "/{document_id}/obligations",
    response_model=list[StructuredObligation],
    summary="Retrieve extracted structured obligations",
)
def get_obligations(document_id: UUID) -> list[StructuredObligation]:
    if not document_store.get_metadata(document_id):
        raise DocumentNotFoundError(f"Document {document_id} was not found.")
    return document_store.get_obligations(document_id)

@router.get(
    "/{document_id}/graph",
    response_model=LegalDocumentGraph,
    summary="Retrieve legal document knowledge graph",
)
def get_graph(document_id: UUID) -> LegalDocumentGraph:
    graph = document_store.get_graph(document_id)
    if not graph:
        raise DocumentNotFoundError(f"Graph for document {document_id} was not found.")
    return graph

@router.get(
    "/{document_id}/summary",
    response_model=DocumentSummary,
    summary="Retrieve structured document summary",
)
def get_summary(document_id: UUID) -> DocumentSummary:
    summary = document_store.get_summary(document_id)
    if not summary:
        raise DocumentNotFoundError(f"Summary for document {document_id} was not found.")
    return summary

@router.post(
    "/{document_id}/ask",
    response_model=QAResponse,
    summary="Ask an evidence-grounded question about the document",
)
async def ask_question(
    document_id: UUID,
    request: QARequest,
    qa_service: QAService = Depends(get_qa_service),
) -> QAResponse:
    return await qa_service.answer_question(document_id, request)

@router.post(
    "/{document_id}/checklist",
    response_model=list[ChecklistItem],
    summary="Generate an actionable pre-signing checklist",
)
async def generate_checklist(
    document_id: UUID,
    checklist_service: ChecklistService = Depends(get_checklist_service),
) -> list[ChecklistItem]:
    return await checklist_service.generate_checklist(document_id)

@router.post(
    "/{document_id}/lawyer-questions",
    response_model=list[LawyerQuestionItem],
    summary="Generate targeted clarification questions for legal counsel",
)
async def generate_lawyer_questions(
    document_id: UUID,
    lawyer_service: LawyerPreparationService = Depends(get_lawyer_prep_service),
) -> list[LawyerQuestionItem]:
    return await lawyer_service.generate_questions(document_id)

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document and clear all associated indexes",
)
def delete_document(
    document_id: UUID,
    doc_service: DocumentService = Depends(get_document_service),
) -> None:
    deleted = doc_service.delete_document(document_id)
    if not deleted:
        raise DocumentNotFoundError(f"Document {document_id} was not found.")
