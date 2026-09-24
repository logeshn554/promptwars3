import json
from uuid import UUID, uuid4

from app.ai.prompts.legal_prompts import CHECKLIST_PROMPT
from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.core.exceptions import DocumentNotFoundError
from app.domain.schemas.document_schemas import ChecklistItem, ProvenanceCitation
from app.repositories.document_store import document_store


class ChecklistService:
    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        self.llm = llm_provider

    async def generate_checklist(self, document_id: UUID) -> list[ChecklistItem]:
        meta = document_store.get_metadata(document_id)
        if not meta:
            raise DocumentNotFoundError(f"Document {document_id} was not found.")

        clauses = document_store.get_clauses(document_id)
        clauses_context = "\n".join([f"- {c.title}: {c.original_text[:150]}" for c in clauses])

        req = LLMRequest(
            messages=[
                LLMMessage(role="system", content=CHECKLIST_PROMPT),
                LLMMessage(role="user", content=f"TASK: CHECKLIST\n\nClauses:\n{clauses_context}"),
            ],
            json_mode=True,
        )

        res = await self.llm.generate(req)
        try:
            items_data = json.loads(res.content)
            if not isinstance(items_data, list):
                items_data = [items_data]
        except Exception:
            items_data = []

        checklist: list[ChecklistItem] = []
        for d in items_data:
            checklist.append(
                ChecklistItem(
                    item_id=uuid4(),
                    task=d.get("task", "Review agreement clause"),
                    category=d.get("category", "General"),
                    completed=False,
                    source_clause=d.get("source_clause"),
                    citation=ProvenanceCitation(
                        document_id=document_id,
                        document_name=meta.filename,
                        page_number=1,
                        clause_number=d.get("source_clause"),
                        excerpt=f"Checklist item linked to {d.get('source_clause', 'agreement')}",
                    ),
                )
            )

        if not checklist:
            # Baseline checklist
            checklist = [
                ChecklistItem(
                    task="Review notice period and resignation obligations",
                    category="Termination",
                    source_clause="Termination Clause",
                ),
                ChecklistItem(
                    task="Confirm base salary disbursement terms and review dates",
                    category="Compensation",
                    source_clause="Payment Clause",
                ),
                ChecklistItem(
                    task="Verify scope of non-compete covenants and geographical restrictions",
                    category="Restrictions",
                    source_clause="Non-Compete Clause",
                )
            ]

        return checklist
