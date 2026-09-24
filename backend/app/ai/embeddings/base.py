import hashlib
from abc import ABC, abstractmethod

import numpy as np


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Generate normalized vector embeddings for a list of strings."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """Generate normalized vector embedding for a single query."""
        pass

class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic semantic hash embedding provider for offline / test environments.
    Maps words to a pseudo-semantic vector space so terms like 'notice', 'resignation',
    and 'termination' have high similarity.
    """
    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def _hash_to_vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimension, dtype=np.float32)
        tokens = text.lower().split()
        if not tokens:
            return vec

        for token in tokens:
            clean = "".join([c for c in token if c.isalnum()])
            if not clean:
                continue
            # Seed reproducible slot from md5
            slot = int(hashlib.md5(clean.encode("utf-8")).hexdigest()[:8], 16) % self.dimension
            vec[slot] += 2.0
            # Also spread energy to neighbors for pseudo-semantic smoothing
            vec[(slot - 1) % self.dimension] += 0.5
            vec[(slot + 1) % self.dimension] += 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        return np.array([self._hash_to_vector(t) for t in texts], dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        return self._hash_to_vector(query)
