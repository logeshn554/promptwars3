import React from 'react';
import { LawyerQuestionItem } from '../types/legal';
import { ShieldCheck, Sparkles } from 'lucide-react';
import { CitationBadge } from '../components/CitationBadge';

interface LawyerPrepProps {
  questions: LawyerQuestionItem[];
  documentName: string;
  loading: boolean;
}

export const LawyerPrep: React.FC<LawyerPrepProps> = ({
  questions,
  documentName,
  loading,
}) => {
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-secondary)' }}>
        <Sparkles size={32} color="#38bdf8" style={{ animation: 'spin 2s linear infinite', margin: '0 auto 12px' }} />
        <p>Synthesizing legal counsel questions from contract clauses...</p>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', color: '#f3f4f6' }}>
          <ShieldCheck size={20} color="#38bdf8" />
          Lawyer Preparation Mode
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '4px', lineHeight: 1.5 }}>
          NyayaLens prepares you for consultations by extracting high-leverage, grounded questions directly from ambiguous, restrictive, or high-liability clauses in <strong style={{ color: '#93c5fd' }}>{documentName}</strong>.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {questions.map((q, idx) => (
          <div
            key={q.question_id}
            style={{
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-md)',
              padding: '18px',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', flexShrink: 0 }}>
                {idx + 1}
              </div>

              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f9fafb', marginBottom: '6px' }}>
                  {q.question}
                </h3>

                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '10px 12px', borderRadius: 'var(--radius-sm)', marginBottom: '8px' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', marginBottom: '2px' }}>
                    Why ask this question:
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {q.context_rationale}
                  </p>
                </div>

                {q.related_clause && (
                  <div style={{ fontSize: '0.75rem', color: '#60a5fa', marginBottom: '6px', fontWeight: 500 }}>
                    Governing Clause: {q.related_clause}
                  </div>
                )}

                {q.citation && <CitationBadge citation={q.citation} />}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
