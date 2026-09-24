# NyayaLens REST API Documentation

The NyayaLens Backend exposes fully documented OpenAPI endpoints under `/api/v1`.
When running locally, interactive Swagger UI is available at `http://127.0.0.1:8000/docs`.

---

## 1. System Health & Configuration

### `GET /api/v1/health`
Checks the operational health and provider state of the platform.
* **Response**:
```json
{
  "status": "healthy",
  "app_name": "NyayaLens",
  "environment": "development",
  "llm_provider": "mock",
  "embedding_provider": "mock"
}
```

---

## 2. Document Management & Ingestion

### `POST /api/v1/documents`
Uploads and processes an agreement (`.pdf`, `.docx`, `.txt`). Performs magic-byte inspection, structure-aware chunking, hybrid index creation, and automatic clause extraction.
* **Request**: `multipart/form-data` with `file: UploadFile`.
* **Response**: `201 Created` with `DocumentMetadata`.

### `GET /api/v1/documents`
Lists all ingested documents in the store.

### `GET /api/v1/documents/{document_id}`
Returns metadata for a specific document.

### `DELETE /api/v1/documents/{document_id}`
Deletes the document, parsed chunks, hybrid index, and all cached analysis.

---

## 3. Legal Intelligence & Analysis

### `GET /api/v1/documents/{document_id}/clauses`
Returns detected legal clauses, categorization (e.g. `TERMINATION`, `NON_COMPETE`), plain-language summaries, and attention flags.

### `GET /api/v1/documents/{document_id}/obligations`
Returns extracted structured obligations (actor, object, deadline, consequence, citation).

### `GET /api/v1/documents/{document_id}/summary`
Returns an executive summary including parties, purpose, key obligations, payments, restrictions, and termination terms.

### `POST /api/v1/documents/{document_id}/checklist`
Generates an actionable pre-signing verification checklist linked to specific contract clauses.

### `POST /api/v1/documents/{document_id}/lawyer-questions`
Generates targeted questions for legal counsel consultation based on ambiguous or restrictive terms.

---

## 4. Evidence-Grounded Q&A

### `POST /api/v1/documents/{document_id}/ask`
Queries the document using hybrid retrieval (Dense Semantic + Sparse BM25) and returns an answer verified against citations.
* **Request Body**:
```json
{
  "question": "What happens if I resign?",
  "plain_language_mode": "standard",
  "top_k": 5
}
```
* **Response**:
```json
{
  "question": "What happens if I resign?",
  "answer": "In the event of voluntary resignation, you must provide ninety (90) days prior written notice according to Clause 11.2.",
  "citations": [
    {
      "document_id": "...",
      "document_name": "employment_agreement_v1.txt",
      "page_number": 1,
      "clause_number": "11.2",
      "excerpt": "In the event of voluntary resignation, Employee shall provide ninety (90) days prior written notice."
    }
  ],
  "confidence": 0.95,
  "insufficient_evidence": false,
  "suggested_questions": ["..."],
  "verified": true,
  "disclaimer": "NyayaLens provides AI-assisted legal information and document explanations..."
}
```

---

## 5. Semantic Contract Comparison

### `POST /api/v1/compare`
Compares two documents (Version A vs. Version B) and detects semantic changes in numbers, deadlines, notice periods, and restrictions.
* **Request Body**:
```json
{
  "doc_a_id": "00000000-0000-0000-0000-000000000001",
  "doc_b_id": "00000000-0000-0000-0000-000000000002"
}
```
