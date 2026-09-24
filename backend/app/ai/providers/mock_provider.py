import json
import re
from typing import Any

from app.ai.providers.base import BaseLLMProvider, LLMRequest, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic offline provider executing structured rule-based and knowledge-based
    synthesis for automated testing, offline CI/CD, and offline hackathon evaluation.
    """
    async def generate(self, request: LLMRequest) -> LLMResponse:
        full_text = " ".join([m.content for m in request.messages])

        # Case 1: Q&A query
        if "TASK: QUESTION ANSWERING" in full_text or "USER QUESTION" in full_text:
            return self._handle_qa_json(full_text)
        # Case 2: Clause extraction
        elif "TASK: EXTRACT CLAUSES" in full_text or "extract all significant legal clauses" in full_text.lower():
            return self._handle_clause_extraction_json(full_text)
        # Case 3: Summary
        elif "TASK: DOCUMENT SUMMARY" in full_text or "structured legal summary" in full_text.lower():
            return self._handle_summary_json(full_text)
        # Case 4: Checklist
        elif "TASK: CHECKLIST" in full_text or "pre-signing or compliance checklist" in full_text.lower():
            return self._handle_checklist_json(full_text)
        # Case 5: Lawyer questions
        elif "TASK: LAWYER QUESTIONS" in full_text or "targeted, grounded questions" in full_text.lower():
            return self._handle_lawyer_questions_json(full_text)
        # Case 6: Comparison
        elif "TASK: DOCUMENT COMPARISON" in full_text or "VERSION A" in full_text:
            return self._handle_comparison_json(full_text)

        # Default fallback answer
        return LLMResponse(
            content="NyayaLens analysis completed based on provided evidence.",
            prompt_tokens=100,
            completion_tokens=50,
            model="mock-legal-v1",
        )

    def _handle_qa_json(self, text: str) -> LLMResponse:
        # Extract the user question specifically if present
        q_match = re.search(r"USER QUESTION:\s*(.*)", text, re.IGNORECASE)
        question_line = q_match.group(1).lower() if q_match else text.lower()

        empty_citations: list[dict[str, Any]] = []
        if "dog food" in question_line or "pet" in question_line or "solar panel" in question_line or "arbitrary non-existent topic" in question_line:
            ans: dict[str, Any] = {
                "answer": "I could not find sufficient information in the uploaded document to answer this reliably.",
                "insufficient_evidence": True,
                "confidence": 0.0,
                "citations": empty_citations,
                "suggested_questions": [
                    "What are the primary termination terms?",
                    "What are the compensation terms?"
                ]
            }
        elif "what happens if i resign" in question_line or "resignation" in question_line or "resign" in question_line:
            ans = {
                "answer": "In the event of voluntary resignation, you must provide ninety (90) days prior written notice according to Clause 11.2.",
                "insufficient_evidence": False,
                "confidence": 0.95,
                "citations": [
                    {
                        "clause_number": "11.2",
                        "page_number": 1,
                        "section_title": "TERMINATION",
                        "excerpt": "In the event of voluntary resignation, Employee shall provide ninety (90) days prior written notice."
                    }
                ],
                "suggested_questions": [
                    "Can the 90-day notice period be waived or bought out?",
                    "What benefits or obligations continue post-resignation?"
                ]
            }
        else:
            ans = {
                "answer": "Based on the retrieved document clauses, the provisions outline specific operational duties and responsibilities for both parties.",
                "insufficient_evidence": False,
                "confidence": 0.85,
                "citations": empty_citations,
                "suggested_questions": ["What are the key obligations?", "What are the dispute terms?"]
            }

        return LLMResponse(content=json.dumps(ans), model="mock-legal-v1")

    def _handle_clause_extraction_json(self, text: str) -> LLMResponse:
        clauses = [
            {
                "category": "TERMINATION",
                "title": "Termination and Notice Period",
                "original_text": "In the event of voluntary resignation, Employee shall provide ninety (90) days prior written notice.",
                "plain_language_explanation": "Either you or the company can end the contract by giving 90 days written notice in advance.",
                "parties": ["Acme Corp", "John Doe"],
                "obligations": ["Provide ninety (90) days prior written notice before termination"],
                "rights": ["Terminate agreement with advance notice"],
                "deadlines": ["90 days notice prior to termination"],
                "financial_implications": ["Salary paid through notice period"],
                "restrictions": ["Must fulfill duties during notice period"],
                "questions_to_clarify": ["Can the employer waive the notice period with pay?"],
                "confidence": 0.92,
                "attention_flags": [
                    {
                        "category": "DEADLINE",
                        "reason": "Extended 90-day notice requirement before termination.",
                        "confidence": 0.95
                    }
                ]
            },
            {
                "category": "NON_COMPETE",
                "title": "Non-Competition Covenant",
                "original_text": "Employee shall not engage in competing business for 12 months post-termination.",
                "plain_language_explanation": "You cannot work for a competing business for 12 months after leaving the company.",
                "parties": ["John Doe"],
                "obligations": ["Refrain from working for competing entities"],
                "rights": list[str](),
                "deadlines": ["12 months post-termination"],
                "financial_implications": list[str](),
                "restrictions": ["Non-compete applies within designated territory"],
                "questions_to_clarify": ["Is the non-compete enforceable in my jurisdiction?"],
                "confidence": 0.94,
                "attention_flags": [
                    {
                        "category": "RESTRICTION",
                        "reason": "12-month post-employment restriction on working in the industry.",
                        "confidence": 0.96
                    }
                ]
            }
        ]
        return LLMResponse(content=json.dumps(clauses), model="mock-legal-v1")

    def _handle_summary_json(self, text: str) -> LLMResponse:
        summary = {
            "document_type": "Employment Agreement",
            "parties": ["Acme Corp", "John Doe"],
            "purpose": "Governs the terms and conditions of employment, duties, compensation, and post-termination restrictions.",
            "important_dates": ["Start Date: October 1, 2026", "Notice Period: 90 days"],
            "key_obligations": ["Perform assigned duties diligently", "Provide 90 days notice for resignation", "Maintain confidentiality"],
            "key_rights": ["Semi-monthly salary payments", "Standard company benefits"],
            "payments": ["Annual salary paid semi-monthly", "Reimbursement of business expenses"],
            "restrictions": ["12-month post-employment non-compete", "Strict non-disclosure of proprietary information"],
            "termination_summary": "At-will employment terminable by either party with 90 days notice or immediately for cause.",
            "dispute_resolution": "Binding arbitration according to rules.",
            "attention_items": [
                {
                    "category": "RESTRICTION",
                    "reason": "12-month non-compete clause restricts post-employment opportunities.",
                    "confidence": 0.95
                },
                {
                    "category": "DEADLINE",
                    "reason": "90-day resignation notice requirement is longer than typical 14-30 day industry standard.",
                    "confidence": 0.92
                }
            ],
            "questions_worth_clarifying": [
                "Is the 90-day notice period negotiable to 30 days?",
                "What specific entities are considered competing under the 12-month restriction?"
            ]
        }
        return LLMResponse(content=json.dumps(summary), model="mock-legal-v1")

    def _handle_checklist_json(self, text: str) -> LLMResponse:
        checklist = [
            {"task": "Verify starting salary, currency, and payment frequency", "category": "Compensation", "source_clause": "Section 3.1"},
            {"task": "Confirm whether 90-day notice period can be reduced prior to signing", "category": "Termination", "source_clause": "Section 11.2"},
            {"task": "Check territory and scope of 12-month non-compete restriction", "category": "Restrictions", "source_clause": "Section 8.1"},
            {"task": "Review IP assignment clause for exclusions on personal side projects", "category": "Intellectual Property", "source_clause": "Section 7.3"},
            {"task": "Confirm confidentiality duration and post-employment survival terms", "category": "Confidentiality", "source_clause": "Section 6.2"},
            {"task": "Check dispute resolution mechanism and required arbitration venue", "category": "Dispute Resolution", "source_clause": "Section 14.1"}
        ]
        return LLMResponse(content=json.dumps(checklist), model="mock-legal-v1")

    def _handle_lawyer_questions_json(self, text: str) -> LLMResponse:
        questions = [
            {
                "question": "Can the 90-day resignation notice period be negotiated down to 30 days?",
                "context_rationale": "90 days is significantly above standard notice and could restrict transitioning to future opportunities.",
                "related_clause": "Clause 11.2 (Termination)"
            },
            {
                "question": "Is the 12-month non-compete clause legally enforceable in our jurisdiction?",
                "context_rationale": "Non-compete agreements are heavily restricted or void in several jurisdictions unless narrowly tailored.",
                "related_clause": "Clause 8.1 (Non-Competition)"
            },
            {
                "question": "Does the Intellectual Property assignment clause carve out side projects developed outside work hours?",
                "context_rationale": "Broad IP assignment clauses might inadvertently encompass personal software developed without company equipment.",
                "related_clause": "Clause 7.3 (Proprietary Rights)"
            },
            {
                "question": "Are indemnification obligations capped at a specific dollar liability limit?",
                "context_rationale": "Uncapped indemnification poses substantial personal or commercial financial exposure.",
                "related_clause": "Clause 12.4 (Indemnification)"
            }
        ]
        return LLMResponse(content=json.dumps(questions), model="mock-legal-v1")

    def _handle_comparison_json(self, text: str) -> LLMResponse:
        comparison = {
            "summary_of_differences": "Version B significantly increases notice period and post-employment restrictions while modifying compensation terms.",
            "added_clauses": ["Section 15 (Data Privacy and AI Usage)"],
            "removed_clauses": ["Section 10.4 (Remote Work Allowance)"],
            "semantic_changes": [
                {
                    "significance": "DEADLINE_CHANGE",
                    "clause_category": "TERMINATION",
                    "topic": "Notice Period",
                    "version_a_text": "Either party may terminate upon 30 days written notice.",
                    "version_b_text": "Either party may terminate upon 90 days written notice.",
                    "description_of_change": "Notice requirement increased by 60 days (from 30 days to 90 days)."
                },
                {
                    "significance": "RESTRICTION_CHANGE",
                    "clause_category": "NON_COMPETE",
                    "topic": "Non-Compete Duration",
                    "version_a_text": "Employee shall not engage in competing business for 6 months post-termination.",
                    "version_b_text": "Employee shall not engage in competing business for 12 months post-termination.",
                    "description_of_change": "Non-compete duration doubled from 6 months to 12 months."
                },
                {
                    "significance": "FINANCIAL_CHANGE",
                    "clause_category": "COMPENSATION",
                    "topic": "Bonus Structure",
                    "version_a_text": "Annual performance bonus of 15% guaranteed upon meeting KPIs.",
                    "version_b_text": "Discretionary performance bonus subject to sole board approval.",
                    "description_of_change": "Shifted bonus from guaranteed KPI-based model to discretionary approval."
                }
            ]
        }
        return LLMResponse(content=json.dumps(comparison), model="mock-legal-v1")
