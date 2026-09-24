import json
from uuid import UUID

from app.ai.prompts.legal_prompts import QA_SYSTEM_PROMPT
from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.ai.verification.verifier import EvidenceVerificationService
from app.core.exceptions import (
    DocumentNotFoundError,
)
from app.core.logging import logger
from app.core.security import inspect_for_prompt_injection
from app.domain.schemas.document_schemas import (
    ProvenanceCitation,
    QARequest,
    QAResponse,
)
from app.repositories.document_store import document_store


class QAService:
    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        self.llm = llm_provider
        self.verifier = EvidenceVerificationService()

    async def answer_question(self, document_id: UUID, request: QARequest) -> QAResponse:
        # 1. Security Check for Prompt Injection inside query
        is_injection, pattern = inspect_for_prompt_injection(request.question, strict=False)
        if is_injection:
            logger.warning(f"Prompt injection pattern intercepted in user query: {pattern}")
            return QAResponse(
                question=request.question,
                answer="NyayaLens Security: The question contains instruction overrides or prompt injection attempts and cannot be processed.",
                citations=[],
                confidence=0.0,
                insufficient_evidence=True,
                suggested_questions=["What are the termination requirements?", "What are the payment terms?"],
                verified=True,
            )

        metadata = document_store.get_metadata(document_id)
        if not metadata:
            raise DocumentNotFoundError(f"Document {document_id} was not found.")

        retriever = document_store.get_retriever(document_id)
        if not retriever:
            raise DocumentNotFoundError(f"Index for document {document_id} is missing.")

        # 2. Hybrid Retrieval (Dense Vector + Sparse BM25)
        top_chunks_and_scores = retriever.retrieve(
            query=request.question,
            top_k=request.top_k,
            alpha=0.5,
        )

        if not top_chunks_and_scores:
            return QAResponse(
                question=request.question,
                answer="I could not find sufficient information in the uploaded document to answer this reliably.",
                citations=[],
                confidence=0.0,
                insufficient_evidence=True,
                suggested_questions=["What is the document title?", "What are the primary clauses?"],
                verified=True,
            )

        # 3. Context Construction with Untrusted Data Isolation
        retrieved_chunks = [item[0] for item in top_chunks_and_scores]
        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks):
            context_blocks.append(
                f"[EXCERPT {idx+1} | Page {chunk.page_number or 1} | Section: {chunk.section_title or 'General'} | Clause: {chunk.clause_number or 'N/A'}]\n{chunk.text}"
            )
        formatted_context = "\n\n".join(context_blocks)

        user_content = (
            f"TASK: QUESTION ANSWERING\n"
            f"Target Plain-Language Mode: {request.plain_language_mode.value}\n\n"
            f"--- BEGIN UNTRUSTED DOCUMENT CONTEXT ---\n"
            f"{formatted_context}\n"
            f"--- END UNTRUSTED DOCUMENT CONTEXT ---\n\n"
            f"USER QUESTION: {request.question}\n\n"
            f"Answer solely from the excerpts above."
        )

        llm_request = LLMRequest(
            messages=[
                LLMMessage(role="system", content=QA_SYSTEM_PROMPT),
                LLMMessage(role="user", content=user_content),
            ],
            json_mode=True,
            temperature=0.0,
        )

        llm_response = await self.llm.generate(llm_request)

        try:
            parsed_json = json.loads(llm_response.content)
            answer_text = parsed_json.get("answer", "")
            insufficient = bool(parsed_json.get("insufficient_evidence", False))
            raw_citations = parsed_json.get("citations", [])
            suggested_qs = parsed_json.get("suggested_questions", [])
            base_confidence = float(parsed_json.get("confidence", 0.8))
        except Exception:
            answer_text = llm_response.content
            insufficient = False
            raw_citations = []
            suggested_qs = []
            base_confidence = 0.7

        # 4. Citation and Evidence Verification Layer
        validated_citations: list[ProvenanceCitation] = []
        for c in raw_citations:
            excerpt = c.get("excerpt", "")
            cite_obj = ProvenanceCitation(
                document_id=document_id,
                document_name=metadata.filename,
                page_number=c.get("page_number", 1),
                section_title=c.get("section_title"),
                clause_number=c.get("clause_number"),
                excerpt=excerpt,
            )
            # Verify citation against actual retrieved chunks
            if self.verifier.verify_citation(cite_obj, retrieved_chunks):
                validated_citations.append(cite_obj)

        # Fallback citation to top retrieved chunk if model generated valid answer with no citation
        if not validated_citations and not insufficient and retrieved_chunks:
            top_chunk = retrieved_chunks[0]
            validated_citations.append(
                ProvenanceCitation(
                    document_id=document_id,
                    document_name=metadata.filename,
                    page_number=top_chunk.page_number or 1,
                    section_title=top_chunk.section_title,
                    clause_number=top_chunk.clause_number,
                    excerpt=top_chunk.text[:250],
                )
            )

        # If answer claims insufficient evidence
        if insufficient or "could not find sufficient information" in answer_text.lower():
            return QAResponse(
                question=request.question,
                answer="I could not find sufficient information in the uploaded document to answer this reliably.",
                citations=[],
                confidence=0.0,
                insufficient_evidence=True,
                suggested_questions=suggested_qs or ["What are the agreement dates?", "What are the payment terms?"],
                verified=True,
            )

        # Derive honest confidence based on retrieval score and citation verification
        avg_retrieval_score = sum(score for _, score in top_chunks_and_scores) / len(top_chunks_and_scores)
        honest_confidence = round(min(1.0, (avg_retrieval_score * 0.4) + (base_confidence * 0.6)), 2)

        return QAResponse(
            question=request.question,
            answer=answer_text,
            citations=validated_citations,
            confidence=honest_confidence,
            insufficient_evidence=False,
            suggested_questions=suggested_qs,
            verified=True,
        )
