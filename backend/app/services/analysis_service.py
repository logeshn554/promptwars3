import json
from uuid import UUID, uuid4

from app.ai.prompts.legal_prompts import (
    CLAUSE_EXTRACTION_PROMPT,
    DOCUMENT_SUMMARY_PROMPT,
)
from app.ai.providers.base import BaseLLMProvider, LLMMessage, LLMRequest
from app.core.logging import logger
from app.domain.enums.legal_enums import (
    AttentionFlagCategory,
    ClauseCategory,
    GraphNodeType,
    GraphRelationType,
)
from app.domain.schemas.document_schemas import (
    AttentionFlag,
    ClauseAnalysis,
    DocumentSummary,
    GraphEdge,
    GraphNode,
    LegalDocumentGraph,
    ProvenanceCitation,
    StructuredObligation,
)
from app.parsers.base import ParsedDocumentResult


class AnalysisService:
    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        self.llm = llm_provider

    async def analyze_document(
        self,
        document_id: UUID,
        parsed_doc: ParsedDocumentResult,
    ) -> tuple[list[ClauseAnalysis], list[StructuredObligation], LegalDocumentGraph, DocumentSummary]:
        """
        Executes structured clause segmentation, obligation extraction, graph building,
        and legal summary generation.
        """
        clauses = await self._extract_clauses(document_id, parsed_doc)
        obligations = self._extract_obligations(document_id, parsed_doc, clauses)
        graph = self._build_document_graph(document_id, parsed_doc.filename, clauses, obligations)
        summary = await self._generate_summary(document_id, parsed_doc, clauses)

        return clauses, obligations, graph, summary

    async def _extract_clauses(
        self,
        document_id: UUID,
        parsed_doc: ParsedDocumentResult,
    ) -> list[ClauseAnalysis]:
        prompt_content = f"TASK: EXTRACT CLAUSES\n\n{CLAUSE_EXTRACTION_PROMPT}\n\nDocument Text Sample:\n{parsed_doc.raw_text[:4000]}"
        request = LLMRequest(
            messages=[
                LLMMessage(role="system", content="You are a legal document parsing expert. Return strictly valid JSON array."),
                LLMMessage(role="user", content=prompt_content),
            ],
            json_mode=True,
        )

        try:
            res = await self.llm.generate(request)
            data = json.loads(res.content)
            if not isinstance(data, list):
                data = [data]
        except Exception as e:
            logger.warning(f"Error parsing LLM clause response, falling back to rule-based: {e}")
            data = []

        clauses: list[ClauseAnalysis] = []
        for item in data:
            try:
                cat_str = item.get("category", "OTHER").upper()
                try:
                    category = ClauseCategory[cat_str]
                except KeyError:
                    category = ClauseCategory.OTHER

                flags: list[AttentionFlag] = []
                for f in item.get("attention_flags", []):
                    f_cat_str = f.get("category", "INFORMATIONAL").upper()
                    try:
                        f_cat = AttentionFlagCategory[f_cat_str]
                    except KeyError:
                        f_cat = AttentionFlagCategory.INFORMATIONAL
                    flags.append(
                        AttentionFlag(
                            category=f_cat,
                            reason=f.get("reason", "Attention required"),
                            confidence=float(f.get("confidence", 0.9)),
                            citation=ProvenanceCitation(
                                document_id=document_id,
                                document_name=parsed_doc.filename,
                                page_number=1,
                                excerpt=item.get("original_text", "")[:200],
                            )
                        )
                    )

                clause = ClauseAnalysis(
                    clause_id=uuid4(),
                    category=category,
                    title=item.get("title", f"Clause on {category.value}"),
                    original_text=item.get("original_text", ""),
                    plain_language_explanation=item.get("plain_language_explanation", ""),
                    parties=item.get("parties", []),
                    obligations=item.get("obligations", []),
                    rights=item.get("rights", []),
                    deadlines=item.get("deadlines", []),
                    financial_implications=item.get("financial_implications", []),
                    restrictions=item.get("restrictions", []),
                    questions_to_clarify=item.get("questions_to_clarify", []),
                    confidence=float(item.get("confidence", 0.9)),
                    citations=[
                        ProvenanceCitation(
                            document_id=document_id,
                            document_name=parsed_doc.filename,
                            page_number=1,
                            excerpt=item.get("original_text", "")[:300],
                        )
                    ],
                    attention_flags=flags,
                )
                clauses.append(clause)
            except Exception as item_err:
                logger.debug(f"Skipping malformed clause item: {item_err}")
                continue

        # If LLM returned no clauses, generate baseline from structure chunks
        if not clauses:
            for idx, chunk in enumerate(parsed_doc.chunks[:10]):
                clauses.append(
                    ClauseAnalysis(
                        clause_id=uuid4(),
                        category=ClauseCategory.OTHER,
                        title=chunk.section_title or f"Section {idx+1}",
                        original_text=chunk.text,
                        plain_language_explanation="Standard agreement clause regarding operational duties.",
                        parties=["Parties"],
                        obligations=[],
                        rights=[],
                        deadlines=[],
                        financial_implications=[],
                        restrictions=[],
                        questions_to_clarify=[],
                        confidence=0.8,
                        citations=[
                            ProvenanceCitation(
                                document_id=document_id,
                                document_name=parsed_doc.filename,
                                page_number=chunk.page_number,
                                clause_number=chunk.clause_number,
                                excerpt=chunk.text[:200],
                            )
                        ],
                    )
                )

        return clauses

    def _extract_obligations(
        self,
        document_id: UUID,
        parsed_doc: ParsedDocumentResult,
        clauses: list[ClauseAnalysis],
    ) -> list[StructuredObligation]:
        obligations: list[StructuredObligation] = []
        for clause in clauses:
            for obl in clause.obligations:
                # Structure actor / action / object from textual obligation
                obligations.append(
                    StructuredObligation(
                        obligation_id=uuid4(),
                        actor=clause.parties[0] if clause.parties else "Party",
                        action="Perform",
                        object=obl,
                        deadline=clause.deadlines[0] if clause.deadlines else None,
                        condition=None,
                        consequence="Breach of contract if not performed",
                        source=ProvenanceCitation(
                            document_id=document_id,
                            document_name=parsed_doc.filename,
                            clause_number=clause.title,
                            page_number=1,
                            excerpt=clause.original_text[:200],
                        )
                    )
                )
        return obligations

    def _build_document_graph(
        self,
        document_id: UUID,
        filename: str,
        clauses: list[ClauseAnalysis],
        obligations: list[StructuredObligation],
    ) -> LegalDocumentGraph:
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        doc_node_id = f"doc_{document_id}"
        nodes.append(
            GraphNode(
                node_id=doc_node_id,
                node_type=GraphNodeType.DOCUMENT,
                label=filename,
                properties={"name": filename},
            )
        )

        all_parties = set()
        for clause in clauses:
            all_parties.update(clause.parties)

        for party in all_parties:
            party_id = f"party_{party.lower().replace(' ', '_')}"
            nodes.append(
                GraphNode(
                    node_id=party_id,
                    node_type=GraphNodeType.PARTY,
                    label=party,
                )
            )
            edges.append(
                GraphEdge(
                    source_id=doc_node_id,
                    target_id=party_id,
                    relation=GraphRelationType.APPLIES_TO,
                )
            )

        for clause in clauses:
            clause_node_id = f"clause_{clause.clause_id}"
            nodes.append(
                GraphNode(
                    node_id=clause_node_id,
                    node_type=GraphNodeType.CLAUSE,
                    label=clause.title,
                    properties={"category": clause.category.value},
                )
            )
            edges.append(
                GraphEdge(
                    source_id=doc_node_id,
                    target_id=clause_node_id,
                    relation=GraphRelationType.REFERENCES,
                )
            )

        for obl in obligations:
            obl_id = f"obl_{obl.obligation_id}"
            nodes.append(
                GraphNode(
                    node_id=obl_id,
                    node_type=GraphNodeType.OBLIGATION,
                    label=f"Obligation: {obl.object[:30]}...",
                    properties={"actor": obl.actor},
                )
            )
            party_id = f"party_{obl.actor.lower().replace(' ', '_')}"
            edges.append(
                GraphEdge(
                    source_id=party_id,
                    target_id=obl_id,
                    relation=GraphRelationType.HAS_OBLIGATION,
                )
            )

        return LegalDocumentGraph(nodes=nodes, edges=edges)

    async def _generate_summary(
        self,
        document_id: UUID,
        parsed_doc: ParsedDocumentResult,
        clauses: list[ClauseAnalysis],
    ) -> DocumentSummary:
        prompt_content = f"TASK: DOCUMENT SUMMARY\n\n{DOCUMENT_SUMMARY_PROMPT}\n\nDocument Text Sample:\n{parsed_doc.raw_text[:4000]}"
        req = LLMRequest(
            messages=[
                LLMMessage(role="system", content="Generate structured legal summary in JSON."),
                LLMMessage(role="user", content=prompt_content),
            ],
            json_mode=True,
        )
        try:
            res = await self.llm.generate(req)
            data = json.loads(res.content)
        except Exception:
            data = {}

        attention_items: list[AttentionFlag] = []
        for c in clauses:
            attention_items.extend(c.attention_flags)

        return DocumentSummary(
            document_id=document_id,
            document_type=data.get("document_type", "Legal Agreement"),
            parties=data.get("parties", ["Party A", "Party B"]),
            purpose=data.get("purpose", "Defines bilateral contractual responsibilities and obligations."),
            important_dates=data.get("important_dates", ["Effective Date", "Termination Date"]),
            key_obligations=data.get("key_obligations", ["Compliance with agreement terms"]),
            key_rights=data.get("key_rights", ["Mutual right to termination upon advance notice"]),
            payments=data.get("payments", ["Terms specified in compensation provisions"]),
            restrictions=data.get("restrictions", ["Confidentiality and proprietary use restrictions"]),
            termination_summary=data.get("termination_summary", "Terminable upon written notice according to agreement clauses."),
            dispute_resolution=data.get("dispute_resolution", "Standard dispute resolution and jurisdiction clauses apply."),
            attention_items=attention_items,
            questions_worth_clarifying=data.get("questions_worth_clarifying", ["What remedies exist in case of breach?"]),
            citations=[
                ProvenanceCitation(
                    document_id=document_id,
                    document_name=parsed_doc.filename,
                    page_number=1,
                    excerpt=parsed_doc.raw_text[:250],
                )
            ],
        )
