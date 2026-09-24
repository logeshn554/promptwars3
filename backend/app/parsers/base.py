from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from app.domain.schemas.document_schemas import DocumentChunk


@dataclass
class ParsedDocumentResult:
    document_id: UUID
    filename: str
    raw_text: str
    page_count: int
    chunks: list[DocumentChunk]
    metadata: dict[str, str | int]

class BaseDocumentParser(ABC):
    """Abstract base parser enforcing structured chunking and provenance preservation."""

    @abstractmethod
    def parse(self, file_path: Path, document_id: UUID, filename: str) -> ParsedDocumentResult:
        """Parse file content into standardized structure with chunk-level metadata."""
        pass
