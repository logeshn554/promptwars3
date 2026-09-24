from typing import Any


class NyayaLensError(Exception):
    """Base exception for all NyayaLens errors."""
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

class UnsupportedFileTypeError(NyayaLensError):
    """Raised when an uploaded file is not supported or fails MIME inspection."""
    pass

class FileTooLargeError(NyayaLensError):
    """Raised when an uploaded file exceeds the configured maximum byte limit."""
    pass

class DocumentParseError(NyayaLensError):
    """Raised when parsing fails on a corrupt or malformed document."""
    pass

class DocumentNotFoundError(NyayaLensError):
    """Raised when the specified document ID does not exist in the store."""
    pass

class RetrievalError(NyayaLensError):
    """Raised when indexing or retrieval pipeline encounters an unrecoverable failure."""
    pass

class LLMProviderError(NyayaLensError):
    """Raised when downstream AI model provider call fails or times out."""
    pass

class InvalidCitationError(NyayaLensError):
    """Raised when citation metadata validation fails post-generation."""
    pass

class InsufficientEvidenceError(NyayaLensError):
    """Raised when document context lacks grounding evidence for a query."""
    pass

class PromptInjectionDetectedError(NyayaLensError):
    """Raised when user query or document contains active prompt injection payloads."""
    pass
