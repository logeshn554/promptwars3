from uuid import UUID

from app.ai.retrieval.hybrid_retriever import HybridLegalRetriever
from app.domain.schemas.document_schemas import (
    ClauseAnalysis,
    DocumentMetadata,
    DocumentSummary,
    LegalDocumentGraph,
    StructuredObligation,
)
from app.parsers.base import ParsedDocumentResult


class DocumentStore:
    """Thread-safe in-memory repository for ingested documents, chunks, indices, and analysis."""
    def __init__(self) -> None:
        self.metadata_store: dict[UUID, DocumentMetadata] = {}
        self.parsed_store: dict[UUID, ParsedDocumentResult] = {}
        self.retrievers: dict[UUID, HybridLegalRetriever] = {}
        self.clauses_store: dict[UUID, list[ClauseAnalysis]] = {}
        self.obligations_store: dict[UUID, list[StructuredObligation]] = {}
        self.graph_store: dict[UUID, LegalDocumentGraph] = {}
        self.summary_store: dict[UUID, DocumentSummary] = {}

    def save_document(
        self,
        metadata: DocumentMetadata,
        parsed: ParsedDocumentResult,
    ) -> None:
        self.metadata_store[metadata.document_id] = metadata
        self.parsed_store[metadata.document_id] = parsed

        # Build and store hybrid retriever index
        retriever = HybridLegalRetriever()
        retriever.index_chunks(parsed.chunks)
        self.retrievers[metadata.document_id] = retriever

    def get_metadata(self, document_id: UUID) -> DocumentMetadata | None:
        return self.metadata_store.get(document_id)

    def list_documents(self) -> list[DocumentMetadata]:
        return list(self.metadata_store.values())

    def get_parsed(self, document_id: UUID) -> ParsedDocumentResult | None:
        return self.parsed_store.get(document_id)

    def get_retriever(self, document_id: UUID) -> HybridLegalRetriever | None:
        return self.retrievers.get(document_id)

    def save_clauses(self, document_id: UUID, clauses: list[ClauseAnalysis]) -> None:
        self.clauses_store[document_id] = clauses

    def get_clauses(self, document_id: UUID) -> list[ClauseAnalysis]:
        return self.clauses_store.get(document_id, [])

    def save_obligations(self, document_id: UUID, obligations: list[StructuredObligation]) -> None:
        self.obligations_store[document_id] = obligations

    def get_obligations(self, document_id: UUID) -> list[StructuredObligation]:
        return self.obligations_store.get(document_id, [])

    def save_graph(self, document_id: UUID, graph: LegalDocumentGraph) -> None:
        self.graph_store[document_id] = graph

    def get_graph(self, document_id: UUID) -> LegalDocumentGraph | None:
        return self.graph_store.get(document_id)

    def save_summary(self, document_id: UUID, summary: DocumentSummary) -> None:
        self.summary_store[document_id] = summary

    def get_summary(self, document_id: UUID) -> DocumentSummary | None:
        return self.summary_store.get(document_id)

    def delete_document(self, document_id: UUID) -> bool:
        if document_id in self.metadata_store:
            del self.metadata_store[document_id]
            self.parsed_store.pop(document_id, None)
            self.retrievers.pop(document_id, None)
            self.clauses_store.pop(document_id, None)
            self.obligations_store.pop(document_id, None)
            self.graph_store.pop(document_id, None)
            self.summary_store.pop(document_id, None)
            return True
        return False

# Global singleton repository
document_store = DocumentStore()
