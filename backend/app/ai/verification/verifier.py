from difflib import SequenceMatcher

from app.domain.schemas.document_schemas import DocumentChunk, ProvenanceCitation


class EvidenceVerificationService:
    """
    Validates model output against actual retrieved document chunks to eliminate hallucinations
    and enforce citation integrity.
    """
    @staticmethod
    def verify_citation(
        citation: ProvenanceCitation,
        grounding_chunks: list[DocumentChunk],
        min_similarity: float = 0.5,
    ) -> bool:
        """
        Ensures that cited excerpt actually corresponds to at least one chunk in the document.
        """
        if not citation.excerpt or not grounding_chunks:
            return False

        norm_excerpt = " ".join(citation.excerpt.lower().split())
        for chunk in grounding_chunks:
            norm_chunk = " ".join(chunk.text.lower().split())
            if norm_excerpt in norm_chunk:
                return True

            # Fuzzy match for minor OCR/formatting variations
            matcher = SequenceMatcher(None, norm_excerpt, norm_chunk)
            match = matcher.find_longest_match(0, len(norm_excerpt), 0, len(norm_chunk))
            if match.size / max(len(norm_excerpt), 1) >= min_similarity:
                return True

        return False

    @classmethod
    def filter_and_validate_citations(
        cls,
        citations: list[ProvenanceCitation],
        grounding_chunks: list[DocumentChunk],
    ) -> list[ProvenanceCitation]:
        """Filters out citations that cannot be verified against document provenance."""
        valid_citations: list[ProvenanceCitation] = []
        for cite in citations:
            if cls.verify_citation(cite, grounding_chunks):
                valid_citations.append(cite)
        return valid_citations
