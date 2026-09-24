from pathlib import Path
from uuid import UUID

from app.core.exceptions import DocumentParseError
from app.domain.schemas.document_schemas import DocumentChunk
from app.parsers.base import BaseDocumentParser, ParsedDocumentResult
from app.parsers.text_parser import chunk_text_structure_aware


class PDFDocumentParser(BaseDocumentParser):
    def parse(self, file_path: Path, document_id: UUID, filename: str) -> ParsedDocumentResult:
        # First try PyMuPDF (fitz) if installed, else fallback to standard pypdf
        try:
            import fitz  # type: ignore

            try:
                doc = fitz.open(file_path)
            except Exception as e:
                raise DocumentParseError(f"Corrupted or invalid PDF {filename}: {str(e)}") from e

            if doc.is_encrypted:
                doc.close()
                raise DocumentParseError(f"PDF {filename} is password-protected or encrypted.")

            page_count = len(doc)
            if page_count == 0:
                doc.close()
                raise DocumentParseError(f"PDF {filename} contains zero pages.")

            all_chunks: list[DocumentChunk] = []
            raw_text_parts: list[str] = []

            try:
                for page_idx in range(page_count):
                    page = doc.load_page(page_idx)
                    page_text = page.get_text("text") or ""
                    raw_text_parts.append(page_text)

                    if page_text.strip():
                        page_chunks = chunk_text_structure_aware(
                            text=page_text,
                            document_id=document_id,
                            page_number=page_idx + 1,
                        )
                        all_chunks.extend(page_chunks)
            finally:
                doc.close()

        except ImportError:
            # Native pypdf fallback (pure python, zero C dependencies)
            import pypdf

            try:
                reader = pypdf.PdfReader(str(file_path))
            except Exception as e:
                raise DocumentParseError(f"Corrupted or invalid PDF {filename}: {str(e)}") from e

            if reader.is_encrypted:
                raise DocumentParseError(f"PDF {filename} is password-protected or encrypted.") from None

            page_count = len(reader.pages)
            if page_count == 0:
                raise DocumentParseError(f"PDF {filename} contains zero pages.") from None

            all_chunks = []
            raw_text_parts = []

            for page_idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                raw_text_parts.append(page_text)

                if page_text.strip():
                    page_chunks = chunk_text_structure_aware(
                        text=page_text,
                        document_id=document_id,
                        page_number=page_idx + 1,
                    )
                    all_chunks.extend(page_chunks)

        full_raw_text = "\n\n".join(raw_text_parts)
        if not full_raw_text.strip():
            raise DocumentParseError(f"PDF {filename} contains no extractable text.")

        return ParsedDocumentResult(
            document_id=document_id,
            filename=filename,
            raw_text=full_raw_text,
            page_count=page_count,
            chunks=all_chunks,
            metadata={"format": "pdf", "page_count": page_count},
        )
