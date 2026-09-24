from app.ai.providers.factory import get_llm_provider
from app.services.checklist_service import ChecklistService
from app.services.comparison_service import ComparisonService
from app.services.document_service import DocumentService
from app.services.lawyer_prep_service import LawyerPreparationService
from app.services.qa_service import QAService


def get_document_service() -> DocumentService:
    return DocumentService()

def get_qa_service() -> QAService:
    return QAService(get_llm_provider())

def get_comparison_service() -> ComparisonService:
    return ComparisonService(get_llm_provider())

def get_checklist_service() -> ChecklistService:
    return ChecklistService(get_llm_provider())

def get_lawyer_prep_service() -> LawyerPreparationService:
    return LawyerPreparationService(get_llm_provider())
