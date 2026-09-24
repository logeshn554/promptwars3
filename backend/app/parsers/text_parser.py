import re
from pathlib import Path
from uuid import UUID

from app.core.exceptions import DocumentParseError
from app.domain.schemas.document_schemas import DocumentChunk
from app.parsers.base import BaseDocumentParser, ParsedDocumentResult

SECTION_REGEX = re.compile(
    r"^(?:SECTION|ARTICLE|CLAUSE)\s+([0-9IVX]+(?:[.\-][0-9A-Za-z]+)*)[:\.\s\-\–]*(.*)$",
    re.IGNORECASE | re.MULTILINE
)
NUMERICAL_CLAUSE_REGEX = re.compile(
    r"^([0-9]+(?:\.[0-9]+)+)\s+(.*)$",
    re.MULTILINE
)

def chunk_text_structure_aware(
    text: str,
    document_id: UUID,
    page_number: int | None = None,
    max_chunk_chars: int = 1200,
    overlap_chars: int = 150,
) -> list[DocumentChunk]:
    """
    Splits text along logical legal boundaries (sections, clauses, numbered paragraphs).
    Avoids splitting mid-clause whenever possible and maintains character offsets.
    """
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[DocumentChunk] = []

    current_section = "General"
    current_clause_num = None
    buffer = ""
    char_cursor = 0
    buffer_start = 0

    for para in paragraphs:
        cleaned_para = para.strip()
        if not cleaned_para:
            continue

        # Detect section / clause headers
        sec_match = SECTION_REGEX.match(cleaned_para)
        num_match = NUMERICAL_CLAUSE_REGEX.match(cleaned_para)

        is_new_section = False
        if sec_match:
            is_new_section = True
            current_clause_num = sec_match.group(1).strip()
            current_section = sec_match.group(2).strip() or f"Section {current_clause_num}"
        elif num_match:
            is_new_section = True
            current_clause_num = num_match.group(1).strip()

        # Flush buffer if new section starts or length exceeded
        if buffer and (is_new_section or len(buffer) + len(cleaned_para) + 2 > max_chunk_chars):
            chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    text=buffer.strip(),
                    page_number=page_number,
                    section_title=current_section,
                    clause_number=current_clause_num,
                    char_start=buffer_start,
                    char_end=buffer_start + len(buffer.strip()),
                )
            )
            buffer = cleaned_para
            buffer_start = char_cursor
        else:
            if not buffer:
                buffer_start = char_cursor
                buffer = cleaned_para
            else:
                buffer += "\n\n" + cleaned_para

        char_cursor += len(cleaned_para) + 2

    if buffer.strip():
        chunks.append(
            DocumentChunk(
                document_id=document_id,
                text=buffer.strip(),
                page_number=page_number,
                section_title=current_section,
                clause_number=current_clause_num,
                char_start=buffer_start,
                char_end=buffer_start + len(buffer.strip()),
            )
        )

    return chunks

class TextDocumentParser(BaseDocumentParser):
    def parse(self, file_path: Path, document_id: UUID, filename: str) -> ParsedDocumentResult:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            raise DocumentParseError(f"Failed to read text file {filename}: {str(e)}") from e

        if not content.strip():
            raise DocumentParseError(f"File {filename} contains no readable text.")

        chunks = chunk_text_structure_aware(content, document_id=document_id, page_number=1)
        return ParsedDocumentResult(
            document_id=document_id,
            filename=filename,
            raw_text=content,
            page_count=1,
            chunks=chunks,
            metadata={"format": "txt", "char_count": len(content)},
        )
