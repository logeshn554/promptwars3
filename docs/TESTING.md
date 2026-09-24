# Testing & Quality Verification

## 1. Testing Strategy

The repository employs a multi-tier testing strategy targeting **>= 85% code coverage** on core business logic without mocking away business rules:

1. **Parser & Chunking Tests (`test_parsers.py`)**: Tests structure-aware section segmentation, empty files, and offset tracking.
2. **Retrieval Tests (`test_retrieval.py`)**: Validates BM25 scoring, stopword pruning, and hybrid vector fusion ranking.
3. **Security & Verification Tests (`test_security_and_verification.py`)**: Tests prompt injection detection, file traversal sanitization, and hallucination rejection in citations.
4. **End-to-End API Workflow Tests (`test_api_workflow.py`)**: Exercises full multi-stage ingestion, clause extraction, grounded Q&A, insufficient evidence, checklist generation, lawyer questions, and version comparison.

---

## 2. Running Automated Tests

```bash
# Backend pytest suite with coverage
cd backend
python -m pytest --cov=app --cov-report=term-missing

# Ruff Linting
python -m ruff check app tests

# Static Type Checking
python -m mypy app
```
