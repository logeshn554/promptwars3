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
import { localLegalApi } from './localApi';

const rawHost = (import.meta.env.VITE_API_BASE_URL || '').trim();
const API_HOST = rawHost.replace(/\/+$/, '');
const BASE_URL = `${API_HOST}/api/v1`;

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || `Request failed with status ${res.status}`);
  }
  return res.json();
}

// Fallback proxy: If running in standalone live deployment (Vercel without Python proxy),
// seamlessly use localLegalApi so the user experiences full live prototype functionality.
export const legalApi = {
  async getHealth(): Promise<{ status: string }> {
    try {
      const res = await fetch(`${BASE_URL}/health`);
      return await handleResponse(res);
    } catch {
      return localLegalApi.getHealth();
    }
  },

  async uploadDocument(file: File): Promise<DocumentMetadata> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${BASE_URL}/documents`, {
        method: 'POST',
        body: formData,
      });
      return await handleResponse<DocumentMetadata>(res);
    } catch {
      return localLegalApi.uploadDocument(file);
    }
  },

  async listDocuments(): Promise<DocumentMetadata[]> {
    try {
      const res = await fetch(`${BASE_URL}/documents`);
      return await handleResponse<DocumentMetadata[]>(res);
    } catch {
      return localLegalApi.listDocuments();
    }
  },

  async getDocument(documentId: UUID): Promise<DocumentMetadata> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${documentId}`);
      return await handleResponse<DocumentMetadata>(res);
    } catch {
      return localLegalApi.getDocument(documentId);
    }
  },

  async getClauses(documentId: UUID): Promise<ClauseAnalysis[]> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${documentId}/clauses`);
      return await handleResponse<ClauseAnalysis[]>(res);
    } catch {
      return localLegalApi.getClauses(documentId);
    }
  },

  async getObligations(documentId: UUID): Promise<StructuredObligation[]> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${documentId}/obligations`);
      return await handleResponse<StructuredObligation[]>(res);
    } catch {
      return localLegalApi.getObligations(documentId);
    }
  },

  async getSummary(documentId: UUID): Promise<DocumentSummary> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${documentId}/summary`);
      return await handleResponse<DocumentSummary>(res);
    } catch {
      return localLegalApi.getSummary(documentId);
    }
  },

  async askQuestion(documentId: UUID, payload: QARequest): Promise<QAResponse> {
    if (API_HOST) {
      try {
        const res = await fetch(`${BASE_URL}/documents/${documentId}/ask`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (res.ok) {
          return await res.json();
        }
        console.warn('Backend responded with error, attempting fallback:', res.status);
      } catch (networkErr) {
        console.warn('Failed to reach live backend at', BASE_URL, networkErr);
      }
    }
    return localLegalApi.askQuestion(documentId, payload);
  },

  async generateChecklist(documentId: UUID): Promise<ChecklistItem[]> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${documentId}/checklist`, {
        method: 'POST',
      });
      return await handleResponse<ChecklistItem[]>(res);
    } catch {
      return localLegalApi.generateChecklist(documentId);
    }
  },

  async generateLawyerQuestions(documentId: UUID): Promise<LawyerQuestionItem[]> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${documentId}/lawyer-questions`, {
        method: 'POST',
      });
      return await handleResponse<LawyerQuestionItem[]>(res);
    } catch {
      return localLegalApi.generateLawyerQuestions(documentId);
    }
  },

  async compareDocuments(docAId: UUID, docBId: UUID): Promise<ComparisonResult> {
    try {
      const res = await fetch(`${BASE_URL}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_a_id: docAId, doc_b_id: docBId }),
      });
      return await handleResponse<ComparisonResult>(res);
    } catch {
      return localLegalApi.compareDocuments(docAId, docBId);
    }
  },

  async deleteDocument(documentId: UUID): Promise<void> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${documentId}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Delete failed');
    } catch {
      await localLegalApi.deleteDocument(documentId);
    }
  },
};
