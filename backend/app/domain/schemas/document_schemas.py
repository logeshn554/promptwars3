from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.enums.legal_enums import (
    AttentionFlagCategory,
    ChangeSignificance,
    ClauseCategory,
    GraphNodeType,
    GraphRelationType,
    PlainLanguageMode,
)


class ProvenanceCitation(BaseModel):
    document_id: UUID
    document_name: str
    page_number: int | None = None
    section_title: str | None = None
    clause_number: str | None = None
    excerpt: str = Field(..., max_length=1000)

class AttentionFlag(BaseModel):
    category: AttentionFlagCategory
    reason: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    citation: ProvenanceCitation

class DocumentChunk(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    text: str
    page_number: int | None = None
    section_title: str | None = None
    clause_number: str | None = None
    char_start: int | None = None
    char_end: int | None = None

class ClauseAnalysis(BaseModel):
    clause_id: UUID = Field(default_factory=uuid4)
    category: ClauseCategory
    title: str
    original_text: str
    plain_language_explanation: str
    parties: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)
    rights: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    financial_implications: list[str] = Field(default_factory=list)
    restrictions: list[str] = Field(default_factory=list)
    questions_to_clarify: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    citations: list[ProvenanceCitation] = Field(default_factory=list)
    attention_flags: list[AttentionFlag] = Field(default_factory=list)

class StructuredObligation(BaseModel):
    obligation_id: UUID = Field(default_factory=uuid4)
    actor: str
    action: str
    object: str
    deadline: str | None = None
    condition: str | None = None
    consequence: str | None = None
    source: ProvenanceCitation

class GraphNode(BaseModel):
    node_id: str
    node_type: GraphNodeType
    label: str
    properties: dict[str, str | int | float | bool] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation: GraphRelationType
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

class LegalDocumentGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)

class DocumentMetadata(BaseModel):
    document_id: UUID = Field(default_factory=uuid4)
    filename: str
    file_type: str
    file_size_bytes: int
    page_count: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_processed: bool = False
    title: str | None = None
    parties: list[str] = Field(default_factory=list)
    document_type: str = "Agreement"

class DocumentSummary(BaseModel):
    document_id: UUID
    document_type: str
    parties: list[str]
    purpose: str
    important_dates: list[str]
    key_obligations: list[str]
    key_rights: list[str]
    payments: list[str]
    restrictions: list[str]
    termination_summary: str
    dispute_resolution: str
    attention_items: list[AttentionFlag]
    questions_worth_clarifying: list[str]
    citations: list[ProvenanceCitation]

class ChecklistItem(BaseModel):
    item_id: UUID = Field(default_factory=uuid4)
    task: str
    category: str
    completed: bool = False
    source_clause: str | None = None
    citation: ProvenanceCitation | None = None

class LawyerQuestionItem(BaseModel):
    question_id: UUID = Field(default_factory=uuid4)
    question: str
    context_rationale: str
    related_clause: str | None = None
    citation: ProvenanceCitation | None = None

class SemanticChange(BaseModel):
    change_id: UUID = Field(default_factory=uuid4)
    significance: ChangeSignificance
    clause_category: ClauseCategory
    topic: str
    version_a_text: str
    version_b_text: str
    description_of_change: str
    evidence_a: ProvenanceCitation | None = None
    evidence_b: ProvenanceCitation | None = None

class ComparisonResult(BaseModel):
    comparison_id: UUID = Field(default_factory=uuid4)
    doc_a_id: UUID
    doc_a_name: str
    doc_b_id: UUID
    doc_b_name: str
    added_clauses: list[str] = Field(default_factory=list)
    removed_clauses: list[str] = Field(default_factory=list)
    semantic_changes: list[SemanticChange] = Field(default_factory=list)
    summary_of_differences: str
    disclaimer: str = "NyayaLens compares contract semantics for informational purposes. This does not constitute legal counsel."

# Q&A Domain Schemas
class QARequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    plain_language_mode: PlainLanguageMode = PlainLanguageMode.STANDARD
    top_k: int = 5

class QAResponse(BaseModel):
    question: str
    answer: str
    citations: list[ProvenanceCitation]
    confidence: float = Field(..., ge=0.0, le=1.0)
    insufficient_evidence: bool = False
    suggested_questions: list[str] = Field(default_factory=list)
    verified: bool = True
    disclaimer: str = "NyayaLens provides AI-assisted legal information and document explanations. It does not provide legal advice and is not a substitute for a qualified legal professional."
