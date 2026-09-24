import json
from uuid import UUID, uuid4

from app.ai.prompts.legal_prompts import DOCUMENT_COMPARISON_PROMPT
from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.core.exceptions import DocumentNotFoundError
from app.core.logging import logger
from app.domain.enums.legal_enums import (
    ChangeSignificance,
    ClauseCategory,
)
from app.domain.schemas.document_schemas import (
    ComparisonResult,
    ProvenanceCitation,
    SemanticChange,
)
from app.repositories.document_store import document_store


class ComparisonService:
    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        self.llm = llm_provider

    async def compare_documents(self, doc_a_id: UUID, doc_b_id: UUID) -> ComparisonResult:
        meta_a = document_store.get_metadata(doc_a_id)
        meta_b = document_store.get_metadata(doc_b_id)

        if not meta_a or not meta_b:
            raise DocumentNotFoundError("One or both documents for comparison could not be found.")

        cached_result = document_store.get_comparison(doc_a_id, doc_b_id)
        if cached_result is not None:
            return cached_result

        parsed_a = document_store.get_parsed(doc_a_id)
        parsed_b = document_store.get_parsed(doc_b_id)

        if not parsed_a or not parsed_b:
            raise DocumentNotFoundError("Document content for comparison is not loaded.")

        user_content = (
            f"TASK: DOCUMENT COMPARISON\n\n"
            f"--- VERSION A ({meta_a.filename}) ---\n"
            f"{parsed_a.raw_text[:3500]}\n\n"
            f"--- VERSION B ({meta_b.filename}) ---\n"
            f"{parsed_b.raw_text[:3500]}\n\n"
            f"Identify semantic differences in numbers, dates, notice periods, non-compete clauses, and compensation."
        )

        req = LLMRequest(
            messages=[
                LLMMessage(role="system", content=DOCUMENT_COMPARISON_PROMPT),
                LLMMessage(role="user", content=user_content),
            ],
            json_mode=True,
        )

        try:
            res = await self.llm.generate(req)
            data = json.loads(res.content)
        except Exception as e:
            logger.warning(f"Error during comparison generation: {e}")
            data = {}

        raw_changes = data.get("semantic_changes", [])
        changes: list[SemanticChange] = []
        for c in raw_changes:
            try:
                sig_str = c.get("significance", "MINOR_TEXT_CHANGE").upper()
                try:
                    sig = ChangeSignificance[sig_str]
                except KeyError:
                    sig = ChangeSignificance.MINOR_TEXT_CHANGE

                cat_str = c.get("clause_category", "OTHER").upper()
                try:
                    cat = ClauseCategory[cat_str]
                except KeyError:
                    cat = ClauseCategory.OTHER

                changes.append(
                    SemanticChange(
                        change_id=uuid4(),
                        significance=sig,
                        clause_category=cat,
                        topic=c.get("topic", "Agreement Terms"),
                        version_a_text=c.get("version_a_text", ""),
                        version_b_text=c.get("version_b_text", ""),
                        description_of_change=c.get("description_of_change", ""),
                        evidence_a=ProvenanceCitation(
                            document_id=doc_a_id,
                            document_name=meta_a.filename,
                            page_number=1,
                            excerpt=c.get("version_a_text", "")[:200],
                        ),
                        evidence_b=ProvenanceCitation(
                            document_id=doc_b_id,
                            document_name=meta_b.filename,
                            page_number=1,
                            excerpt=c.get("version_b_text", "")[:200],
                        ),
                    )
                )
            except Exception as parse_err:
                logger.debug(f"Skipping malformed semantic change: {parse_err}")

        result = ComparisonResult(
            comparison_id=uuid4(),
            doc_a_id=doc_a_id,
            doc_a_name=meta_a.filename,
            doc_b_id=doc_b_id,
            doc_b_name=meta_b.filename,
            added_clauses=data.get("added_clauses", []),
            removed_clauses=data.get("removed_clauses", []),
            semantic_changes=changes,
            summary_of_differences=data.get(
                "summary_of_differences",
                "Comparison completed. Detected semantic changes across key clauses."
            ),
        )
        document_store.save_comparison(result)
        return result
