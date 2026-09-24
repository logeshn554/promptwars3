import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { DocumentManager } from './features/DocumentManager';
import { AnalysisViewer } from './features/AnalysisViewer';
import { DocumentQA } from './features/DocumentQA';
import { DocumentCompare } from './features/DocumentCompare';
import { ChecklistViewer } from './features/ChecklistViewer';
import { LawyerPrep } from './features/LawyerPrep';
import { legalApi } from './services/api';
import {
  DocumentMetadata,
  ClauseAnalysis,
  StructuredObligation,
  DocumentSummary,
  ChecklistItem,
  LawyerQuestionItem,
  PlainLanguageMode,
} from './types/legal';
import { ShieldAlert, AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('documents');
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  // Active document data
  const [summary, setSummary] = useState<DocumentSummary | null>(null);
  const [clauses, setClauses] = useState<ClauseAnalysis[]>([]);
  const [obligations, setObligations] = useState<StructuredObligation[]>([]);
  const [checklist, setChecklist] = useState<ChecklistItem[]>([]);
  const [lawyerQuestions, setLawyerQuestions] = useState<LawyerQuestionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [globalError, setGlobalError] = useState<string | null>(null);

  // Initial load
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await legalApi.listDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !selectedDocId) {
        selectDocument(docs[0].document_id);
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const selectDocument = async (id: string) => {
    setSelectedDocId(id);
    setLoading(true);
    setGlobalError(null);
    try {
      const [sum, cls, obls, chk, lq] = await Promise.all([
        legalApi.getSummary(id).catch(() => null),
        legalApi.getClauses(id).catch(() => []),
        legalApi.getObligations(id).catch(() => []),
        legalApi.generateChecklist(id).catch(() => []),
        legalApi.generateLawyerQuestions(id).catch(() => []),
      ]);
      setSummary(sum);
      setClauses(cls);
      setObligations(obls);
      setChecklist(chk);
      setLawyerQuestions(lq);
    } catch (err: unknown) {
      setGlobalError(err instanceof Error ? err.message : 'Error loading document data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const meta = await legalApi.uploadDocument(file);
      await loadDocuments();
      await selectDocument(meta.document_id);
      setActiveTab('analysis');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    await legalApi.deleteDocument(id);
    if (selectedDocId === id) {
      setSelectedDocId(null);
      setSummary(null);
      setClauses([]);
    }
    await loadDocuments();
  };

  const activeDoc = documents.find((d) => d.document_id === selectedDocId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} documentCount={documents.length} />

      {/* Main Content Area */}
      <main style={{ flex: 1, maxWidth: '1280px', width: '100%', margin: '0 auto', padding: '24px' }}>
        {globalError && (
          <div style={{ marginBottom: '20px', padding: '12px 16px', borderRadius: 'var(--radius-md)', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#fda4af', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} />
            <span>{globalError}</span>
          </div>
        )}

        {/* Tab Routing */}
        {activeTab === 'documents' && (
          <DocumentManager
            documents={documents}
            selectedDocId={selectedDocId}
            onSelectDoc={selectDocument}
            onUpload={handleUpload}
            onDelete={handleDelete}
            loading={loading}
          />
        )}

        {activeTab === 'analysis' && (
          activeDoc ? (
            <AnalysisViewer summary={summary} clauses={clauses} obligations={obligations} loading={loading} />
          ) : (
            <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Please upload or select a document first in the Documents tab.
            </div>
          )
        )}

        {activeTab === 'qa' && (
          activeDoc ? (
            <DocumentQA
              documentName={activeDoc.filename}
              onAsk={(q: string, m: PlainLanguageMode) =>
                legalApi.askQuestion(activeDoc.document_id, { question: q, plain_language_mode: m })
              }
            />
          ) : (
            <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Please upload or select a document first in the Documents tab.
            </div>
          )
        )}

        {activeTab === 'compare' && (
          <DocumentCompare documents={documents} onCompare={legalApi.compareDocuments} />
        )}

        {activeTab === 'checklist' && (
          activeDoc ? (
            <ChecklistViewer
              items={checklist}
              onRefresh={async () => {
                const refreshed = await legalApi.generateChecklist(activeDoc.document_id);
                setChecklist(refreshed);
              }}
              loading={loading}
            />
          ) : (
            <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Please upload or select a document first in the Documents tab.
            </div>
          )
        )}

        {activeTab === 'lawyer' && (
          activeDoc ? (
            <LawyerPrep questions={lawyerQuestions} documentName={activeDoc.filename} loading={loading} />
          ) : (
            <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Please upload or select a document first in the Documents tab.
            </div>
          )
        )}

        {activeTab === 'about' && (
          <div className="glass-panel" style={{ padding: '32px' }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '14px', color: '#f3f4f6' }}>
              About NyayaLens Legal Intelligence
            </h2>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '18px' }}>
              NyayaLens is an evidence-grounded Legal Document Intelligence platform designed to simplify complex legal agreements, detect critical obligations and restrictions, compare contract versions, and arm individuals with actionable clarity before speaking to legal professionals.
            </p>
            <div style={{ background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: 'var(--radius-md)', padding: '16px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#93c5fd', fontWeight: 600, marginBottom: '6px' }}>
                <ShieldAlert size={18} />
                <span>Legal & Compliance Disclaimer</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#e2e8f0', lineHeight: 1.5 }}>
                NyayaLens provides AI-assisted legal information and document explanations. It does not provide legal advice and is not a substitute for a qualified legal professional. Never make binding legal commitments without consultation from a licensed attorney.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Global Accessibility-Compliant Footer with Mandatory Disclaimer */}
      <footer style={{ borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-secondary)', padding: '16px 24px', textAlign: 'center' }}>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          NyayaLens provides AI-assisted legal information and document explanations. It does not provide legal advice and is not a substitute for a qualified legal professional.
        </p>
      </footer>
    </div>
  );
};
