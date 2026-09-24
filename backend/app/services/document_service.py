from uuid import UUID, uuid4

from fastapi import UploadFile

from app.ai.providers.factory import get_llm_provider
from app.core.config import settings
from app.core.exceptions import (
    DocumentNotFoundError,
    DocumentParseError,
    UnsupportedFileTypeError,
)
from app.core.logging import logger
from app.core.security import sanitize_filename, validate_file_metadata
from app.domain.schemas.document_schemas import DocumentMetadata
from app.parsers.factory import parse_document
from app.repositories.document_store import document_store
from app.services.analysis_service import AnalysisService


class DocumentService:
    def __init__(self) -> None:
        self.llm = get_llm_provider()
        self.analysis_service = AnalysisService(self.llm)

    async def upload_and_process_document(self, file: UploadFile) -> DocumentMetadata:
        if not file.filename:
            raise UnsupportedFileTypeError("File upload missing filename.")

        safe_name = sanitize_filename(file.filename)
        document_id = uuid4()

        # Read header bytes for magic bytes verification
        header_bytes = await file.read(2048)
        # Read rest of content
        rest_bytes = await file.read()
        full_content = header_bytes + rest_bytes
        file_size = len(full_content)

        ext = validate_file_metadata(
            filename=safe_name,
            file_size=file_size,
            content_bytes=header_bytes,
        )

        settings.setup_directories()
        temp_file_path = settings.TEMP_DIR / f"{document_id}_{safe_name}"

        try:
            with open(temp_file_path, "wb") as f:
                f.write(full_content)

            # Parse document structure into chunks
            parsed_result = parse_document(
                file_path=temp_file_path,
                document_id=document_id,
                filename=safe_name,
            )

            metadata = DocumentMetadata(
                document_id=document_id,
                filename=safe_name,
                file_type=ext,
                file_size_bytes=file_size,
                page_count=parsed_result.page_count,
                is_processed=True,
                title=safe_name.rsplit(".", 1)[0].replace("_", " ").title(),
            )

            # Store document and build hybrid retrieval index
            document_store.save_document(metadata=metadata, parsed=parsed_result)

            # Perform structured legal analysis (clauses, obligations, graph, summary)
            clauses, obligations, graph, summary = await self.analysis_service.analyze_document(
                document_id=document_id,
                parsed_doc=parsed_result,
            )

            document_store.save_clauses(document_id, clauses)
            document_store.save_obligations(document_id, obligations)
            document_store.save_graph(document_id, graph)
            document_store.save_summary(document_id, summary)

            logger.info(f"Successfully processed document {document_id} ({safe_name}) with {len(clauses)} clauses.")
            return metadata

        except Exception as e:
            logger.error(f"Error processing document {safe_name}: {str(e)}")
            raise DocumentParseError(f"Failed to process document {safe_name}: {str(e)}") from e
        finally:
            # Clean up temporary file on disk (privacy & data minimization)
            if temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except Exception as unlink_err:
                    logger.debug(f"Failed to delete temp file {temp_file_path}: {unlink_err}")

    def get_document_metadata(self, document_id: UUID) -> DocumentMetadata:
        meta = document_store.get_metadata(document_id)
        if not meta:
            raise DocumentNotFoundError(f"Document {document_id} was not found.")
        return meta

    def list_documents(self) -> list[DocumentMetadata]:
        return document_store.list_documents()

    def delete_document(self, document_id: UUID) -> bool:
        return document_store.delete_document(document_id)
