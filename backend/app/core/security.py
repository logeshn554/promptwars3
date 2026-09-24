import re
import unicodedata
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import (
    FileTooLargeError,
    PromptInjectionDetectedError,
    UnsupportedFileTypeError,
)

# Common prompt injection signatures and jailbreak directives
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"(?i)system\s+override",
    r"(?i)reveal\s+(the\s+)?(system\s+prompt|api\s+key|environment\s+variables)",
    r"(?i)print\s+(the\s+)?(api[_\s]?key|env|environ)",
    r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
    r"(?i)disregard\s+(all\s+)?prior\s+directives",
    r"(?i)bypass\s+all\s+(security|safety|rules)",
    r"(?i)act\s+as\s+an\s+unrestricted\s+ai",
]

_COMPILED_INJECTION_REGEX = [re.compile(p) for p in INJECTION_PATTERNS]

MAGIC_BYTES = {
    ".pdf": b"%PDF-",
    ".docx": b"PK\x03\x04",
}

def sanitize_filename(filename: str) -> str:
    """
    Sanitize uploaded filename against directory traversal, absolute path injection,
    null bytes, and path spoofing.
    """
    if not filename:
        return "unnamed_document.txt"

    # Strip null bytes and control characters
    cleaned = filename.replace("\x00", "").replace("\r", "").replace("\n", "")
    # Normalize unicode
    cleaned = unicodedata.normalize("NFKD", cleaned)
    # Extract basename only to prevent traversal
    name = Path(cleaned).name

    # Remove traversal sequences
    name = re.sub(r"\.\.+", ".", name)
    # Allow alphanumeric, dashes, underscores, and single dots
    safe_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)
    if not safe_name or safe_name.startswith("."):
        safe_name = f"doc_{safe_name.lstrip('.')}"
    return safe_name

def validate_file_metadata(filename: str, file_size: int, content_bytes: bytes | None = None) -> str:
    """
    Validates file extension, size, and magic bytes.
    Returns the validated normalized extension.
    """
    if file_size <= 0:
        raise UnsupportedFileTypeError("Uploaded file is empty (0 bytes).")

    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise FileTooLargeError(
            f"File size {file_size} bytes exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_BYTES} bytes."
        )

    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Extension '{ext}' is not supported. Allowed extensions: {settings.ALLOWED_EXTENSIONS}"
        )

    if content_bytes and ext in MAGIC_BYTES:
        magic = MAGIC_BYTES[ext]
        if not content_bytes.startswith(magic):
            raise UnsupportedFileTypeError(
                f"File content does not match expected magic bytes header for {ext}."
            )

    return ext

def inspect_for_prompt_injection(text: str, strict: bool = False) -> tuple[bool, str | None]:
    """
    Inspects text for prompt injection signatures.
    Returns (has_injection, detected_pattern_description).
    """
    for regex in _COMPILED_INJECTION_REGEX:
        match = regex.search(text)
        if match:
            if strict:
                raise PromptInjectionDetectedError(
                    f"Prompt injection pattern detected: '{match.group(0)}'"
                )
            return True, match.group(0)
    return False, None
