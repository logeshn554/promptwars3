import {
  DocumentMetadata,
  ClauseAnalysis,
  StructuredObligation,
  DocumentSummary,
  QARequest,
  QAResponse,
  ChecklistItem,
  LawyerQuestionItem,
  ComparisonResult,
  UUID,
} from '../types/legal';

const BASE_URL = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export const legalApi = {
  async getHealth(): Promise<{ status: string }> {
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse(res);
  },

  async uploadDocument(file: File): Promise<DocumentMetadata> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${BASE_URL}/documents`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<DocumentMetadata>(res);
  },

  async listDocuments(): Promise<DocumentMetadata[]> {
    const res = await fetch(`${BASE_URL}/documents`);
    return handleResponse<DocumentMetadata[]>(res);
  },

  async getDocument(documentId: UUID): Promise<DocumentMetadata> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}`);
    return handleResponse<DocumentMetadata>(res);
  },

  async getClauses(documentId: UUID): Promise<ClauseAnalysis[]> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/clauses`);
    return handleResponse<ClauseAnalysis[]>(res);
  },

  async getObligations(documentId: UUID): Promise<StructuredObligation[]> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/obligations`);
    return handleResponse<StructuredObligation[]>(res);
  },

  async getSummary(documentId: UUID): Promise<DocumentSummary> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/summary`);
    return handleResponse<DocumentSummary>(res);
  },

  async askQuestion(documentId: UUID, payload: QARequest): Promise<QAResponse> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<QAResponse>(res);
  },

  async generateChecklist(documentId: UUID): Promise<ChecklistItem[]> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/checklist`, {
      method: 'POST',
    });
    return handleResponse<ChecklistItem[]>(res);
  },

  async generateLawyerQuestions(documentId: UUID): Promise<LawyerQuestionItem[]> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/lawyer-questions`, {
      method: 'POST',
    });
    return handleResponse<LawyerQuestionItem[]>(res);
  },

  async compareDocuments(docAId: UUID, docBId: UUID): Promise<ComparisonResult> {
    const res = await fetch(`${BASE_URL}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doc_a_id: docAId, doc_b_id: docBId }),
    });
    return handleResponse<ComparisonResult>(res);
  },

  async deleteDocument(documentId: UUID): Promise<void> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      throw new Error(`Failed to delete document: ${res.status}`);
    }
  },
};
