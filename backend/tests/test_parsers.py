from pathlib import Path
from uuid import uuid4

import pytest

from app.core.exceptions import DocumentParseError
from app.parsers.factory import parse_document
from app.parsers.text_parser import chunk_text_structure_aware


def test_structure_aware_chunking() -> None:
    doc_id = uuid4()
    sample_text = """
SECTION 1: DEFINITIONS
In this agreement, terms shall have their assigned meanings.

SECTION 2: TERMINATION AND NOTICE
Either party may terminate this agreement upon 90 days written notice.
Failure to give notice constitutes breach.

SECTION 3: COMPENSATION
Base compensation shall be disbursed semi-monthly.
"""
    chunks = chunk_text_structure_aware(sample_text, document_id=doc_id, page_number=1)
    assert len(chunks) >= 3
    assert any("TERMINATION" in (c.section_title or "") for c in chunks)
    assert any(c.clause_number in ["1", "2", "3"] for c in chunks)

def test_text_parser(tmp_path: Path) -> None:
    doc_id = uuid4()
    p = tmp_path / "agreement.txt"
    p.write_text("SECTION 11.2: RESIGNATION\nEmployee shall provide 90 days written notice.", encoding="utf-8")

    result = parse_document(p, document_id=doc_id, filename="agreement.txt")
    assert result.document_id == doc_id
    assert len(result.chunks) > 0
    assert "90 days" in result.raw_text

def test_empty_text_file_error(tmp_path: Path) -> None:
    doc_id = uuid4()
    p = tmp_path / "empty.txt"
    p.write_text("   \n   ", encoding="utf-8")

    with pytest.raises(DocumentParseError):
        parse_document(p, document_id=doc_id, filename="empty.txt")
