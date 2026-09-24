from uuid import uuid4

from app.ai.embeddings.base import MockEmbeddingProvider
from app.ai.retrieval.hybrid_retriever import BM25Retriever, HybridLegalRetriever
from app.domain.schemas.document_schemas import DocumentChunk


def test_bm25_retriever_scoring() -> None:
    corpus = [
        "The termination notice period is 90 days for voluntary resignation.",
        "Intellectual property rights are assigned exclusively to the company.",
        "Compensation is paid semi-monthly according to the schedule.",
    ]
    bm25 = BM25Retriever()
    bm25.fit(corpus)
    scores = bm25.score("resignation notice")
    assert scores[0] > scores[1]
    assert scores[0] > scores[2]

def test_hybrid_retriever_ranking() -> None:
    doc_id = uuid4()
    chunks = [
        DocumentChunk(
            document_id=doc_id,
            text="Employee may terminate with ninety (90) days advance notice.",
            page_number=7,
            clause_number="11.2",
            section_title="Termination",
        ),
        DocumentChunk(
            document_id=doc_id,
            text="Non-compete covenant restricts competition for twelve (12) months.",
            page_number=5,
            clause_number="8.1",
            section_title="Restrictive Covenants",
        ),
        DocumentChunk(
            document_id=doc_id,
            text="Salary details are kept confidential under proprietary rules.",
            page_number=3,
            clause_number="3.2",
            section_title="Compensation",
        ),
    ]

    retriever = HybridLegalRetriever(MockEmbeddingProvider(dimension=64))
    retriever.index_chunks(chunks)

    results = retriever.retrieve(query="what is the notice period for resignation", top_k=2, alpha=0.5)
    assert len(results) <= 2
    top_chunk, score = results[0]
    assert "ninety" in top_chunk.text or "notice" in top_chunk.text
    assert score > 0.0
