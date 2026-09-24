from pathlib import Path
from uuid import UUID

from app.core.exceptions import UnsupportedFileTypeError
from app.parsers.base import BaseDocumentParser, ParsedDocumentResult
from app.parsers.docx_parser import DocxDocumentParser
from app.parsers.pdf_parser import PDFDocumentParser
from app.parsers.text_parser import TextDocumentParser

_PARSERS: dict[str, BaseDocumentParser] = {
    ".pdf": PDFDocumentParser(),
    ".docx": DocxDocumentParser(),
    ".txt": TextDocumentParser(),
}

def get_parser_for_extension(ext: str) -> BaseDocumentParser:
    normalized = ext.lower()
    if normalized not in _PARSERS:
        raise UnsupportedFileTypeError(f"No parser registered for extension: {normalized}")
    return _PARSERS[normalized]

def parse_document(file_path: Path, document_id: UUID, filename: str) -> ParsedDocumentResult:
    ext = file_path.suffix.lower()
    parser = get_parser_for_extension(ext)
    return parser.parse(file_path=file_path, document_id=document_id, filename=filename)
