import math
import re
from collections import Counter

import numpy as np

from app.ai.embeddings.base import BaseEmbeddingProvider, MockEmbeddingProvider
from app.domain.schemas.document_schemas import DocumentChunk


class BM25Retriever:
    """In-memory BM25 Okapi keyword retriever for legal search."""
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.corpus: list[list[str]] = []
        self.doc_lengths: list[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: dict[str, int] = {}
        self.idf: dict[str, float] = {}

    def fit(self, documents: list[str]) -> None:
        self.corpus = [self._tokenize(doc) for doc in documents]
        self.doc_lengths = [len(doc) for doc in self.corpus]
        total_tokens = sum(self.doc_lengths)
        num_docs = len(self.corpus)
        self.avg_doc_len = (total_tokens / num_docs) if num_docs > 0 else 0.0

        self.doc_freqs = {}
        for doc in self.corpus:
            unique_terms = set(doc)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.idf = {}
        for term, freq in self.doc_freqs.items():
            # Standard Lucene-style smoothed IDF
            self.idf[term] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1.0)

    STOPWORDS = {
        "a", "an", "the", "in", "on", "at", "for", "to", "of", "with", "by", "from",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "and", "or", "but", "if", "what", "which", "who", "whom",
        "this", "that", "these", "those", "it", "its"
    }

    def _tokenize(self, text: str) -> list[str]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        return [t for t in tokens if t not in self.STOPWORDS]

    def score(self, query: str) -> np.ndarray:
        q_tokens = self._tokenize(query)
        num_docs = len(self.corpus)
        scores = np.zeros(num_docs, dtype=np.float32)
        if num_docs == 0 or self.avg_doc_len == 0:
            return scores

        for idx, doc in enumerate(self.corpus):
            doc_len = self.doc_lengths[idx]
            counts = Counter(doc)
            doc_score = 0.0
            for q_term in q_tokens:
                if q_term not in counts:
                    continue
                tf = counts[q_term]
                idf = self.idf.get(q_term, 0.0)
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                doc_score += idf * (numerator / denominator)
            scores[idx] = doc_score

        # Normalize to [0, 1] range if max > 0
        max_score = scores.max()
        if max_score > 0:
            scores /= max_score
        return scores

class HybridLegalRetriever:
    """
    Hybrid retriever combining dense vector cosine similarity and sparse BM25 keyword matching,
    followed by deduplication and reranking.
    """
    def __init__(self, embedding_provider: BaseEmbeddingProvider | None = None) -> None:
        self.embedding_provider = embedding_provider or MockEmbeddingProvider()
        self.chunks: list[DocumentChunk] = []
        self.embeddings: np.ndarray | None = None
        self.bm25 = BM25Retriever()

    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks
        if not chunks:
            self.embeddings = None
            return

        texts = [chunk.text for chunk in chunks]
        self.embeddings = self.embedding_provider.embed_texts(texts)
        self.bm25.fit(texts)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.5,
    ) -> list[tuple[DocumentChunk, float]]:
        """
        Retrieves top_k chunks using hybrid score = alpha * dense + (1 - alpha) * sparse.
        Returns list of (DocumentChunk, relevance_score).
        """
        if not self.chunks or self.embeddings is None:
            return []

        # 1. Dense vector similarity
        q_vec = self.embedding_provider.embed_query(query)
        # Cosine similarity (embeddings are normalized)
        dense_scores = np.dot(self.embeddings, q_vec)
        # Shift [-1, 1] to [0, 1]
        dense_scores = (dense_scores + 1.0) / 2.0

        # 2. Sparse BM25 keyword scores
        bm25_scores = self.bm25.score(query)

        # 3. Hybrid fusion
        combined_scores = (alpha * dense_scores) + ((1.0 - alpha) * bm25_scores)
        top_indices = np.argsort(combined_scores)[::-1][:top_k]

        results: list[tuple[DocumentChunk, float]] = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(combined_scores[idx])))

        return results
