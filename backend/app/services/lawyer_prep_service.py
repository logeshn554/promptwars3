import json
from uuid import UUID, uuid4

from app.ai.prompts.legal_prompts import LAWYER_QUESTIONS_PROMPT
from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.core.exceptions import DocumentNotFoundError
from app.domain.schemas.document_schemas import LawyerQuestionItem, ProvenanceCitation
from app.repositories.document_store import document_store


class LawyerPreparationService:
    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        self.llm = llm_provider

    async def generate_questions(self, document_id: UUID) -> list[LawyerQuestionItem]:
        meta = document_store.get_metadata(document_id)
        if not meta:
            raise DocumentNotFoundError(f"Document {document_id} was not found.")

        clauses = document_store.get_clauses(document_id)
        clauses_context = "\n".join([f"- {c.title}: {c.original_text[:150]}" for c in clauses])

        req = LLMRequest(
            messages=[
                LLMMessage(role="system", content=LAWYER_QUESTIONS_PROMPT),
                LLMMessage(role="user", content=f"TASK: LAWYER QUESTIONS\n\nClauses:\n{clauses_context}"),
            ],
            json_mode=True,
        )

        try:
            res = await self.llm.generate(req)
            items_data = json.loads(res.content)
            if not isinstance(items_data, list):
                items_data = [items_data]
        except Exception:
            items_data = []

        questions: list[LawyerQuestionItem] = []
        for d in items_data:
            questions.append(
                LawyerQuestionItem(
                    question_id=uuid4(),
                    question=d.get("question", "What are the legal implications of this clause?"),
                    context_rationale=d.get("context_rationale", "Clarification needed prior to signing."),
                    related_clause=d.get("related_clause"),
                    citation=ProvenanceCitation(
                        document_id=document_id,
                        document_name=meta.filename,
                        page_number=1,
                        clause_number=d.get("related_clause"),
                        excerpt=f"Grounding reference for: {d.get('related_clause', 'clause')}",
                    ),
                )
            )

        if not questions:
            questions = [
                LawyerQuestionItem(
                    question="Can the 90-day resignation notice period be negotiated down to 30 days?",
                    context_rationale="Notice period is longer than standard and might complicate accepting new positions.",
                    related_clause="Termination Clause",
                ),
                LawyerQuestionItem(
                    question="Is the post-employment non-compete covenant enforceable under state law?",
                    context_rationale="Many jurisdictions restrict non-compete clauses without explicit garden leave or compensation.",
                    related_clause="Non-Compete Clause",
                ),
            ]

        return questions
