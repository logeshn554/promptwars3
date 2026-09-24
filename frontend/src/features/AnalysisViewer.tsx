import React, { useState } from 'react';
import { ClauseAnalysis, DocumentSummary, StructuredObligation } from '../types/legal';
import { CitationBadge } from '../components/CitationBadge';
import { AlertTriangle, Clock, DollarSign, Filter, ShieldAlert, Sparkles } from 'lucide-react';

interface AnalysisViewerProps {
  summary: DocumentSummary | null;
  clauses: ClauseAnalysis[];
  obligations: StructuredObligation[];
  loading: boolean;
}

export const AnalysisViewer: React.FC<AnalysisViewerProps> = ({
  summary,
  clauses,
  obligations,
  loading,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-secondary)' }}>
        <Sparkles size={32} color="#60a5fa" style={{ animation: 'spin 2s linear infinite', margin: '0 auto 12px' }} />
        <p>Analyzing document structure, extracting clauses and attention flags...</p>
      </div>
    );
  }

  const categories = ['ALL', ...Array.from(new Set(clauses.map((c) => c.category)))];
  const filteredClauses = selectedCategory === 'ALL'
    ? clauses
    : clauses.filter((c) => c.category === selectedCategory);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Executive Summary Card */}
      {summary && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f3f4f6' }}>
              {summary.document_type}
            </h2>
            <div style={{ display: 'flex', gap: '6px' }}>
              {summary.parties.map((p, idx) => (
                <span key={idx} className="badge badge-info">{p}</span>
              ))}
            </div>
          </div>

          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '18px', lineHeight: 1.6 }}>
            {summary.purpose}
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
            <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#93c5fd', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock size={16} /> Important Dates & Notice
              </div>
              <ul style={{ paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {summary.important_dates.map((d, i) => <li key={i}>{d}</li>)}
              </ul>
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fde68a', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <DollarSign size={16} /> Financial Implications
              </div>
              <ul style={{ paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {summary.payments.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fca5a5', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <ShieldAlert size={16} /> Restrictions & Non-Compete
              </div>
              <ul style={{ paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                {summary.restrictions.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Clauses Section with Category Filter */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Detected Clauses & Attention Flags</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Structured breakdown with honest confidence and plain-language explanations.</p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} color="var(--text-muted)" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              aria-label="Filter clauses by category"
              style={{
                background: 'var(--bg-secondary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 12px',
                fontSize: '0.85rem',
              }}
            >
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filteredClauses.map((clause) => (
            <div
              key={clause.clause_id}
              style={{
                background: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-md)',
                padding: '18px',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className="badge badge-info">{clause.category}</span>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>{clause.title}</h4>
                </div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Confidence: {Math.round(clause.confidence * 100)}%
                </span>
              </div>

              {/* Plain Language Explanation */}
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8', textTransform: 'uppercase', marginBottom: '2px' }}>
                  Plain-Language Summary
                </div>
                <p style={{ fontSize: '0.85rem', color: '#e2e8f0', lineHeight: 1.5 }}>
                  {clause.plain_language_explanation}
                </p>
              </div>

              {/* Original Legal Excerpt */}
              <div style={{ marginBottom: '12px', background: 'rgba(0,0,0,0.2)', padding: '10px 12px', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '2px' }}>
                  Original Legal Text
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic', lineHeight: 1.4 }}>
                  "{clause.original_text}"
                </p>
              </div>

              {/* Attention Flags */}
              {clause.attention_flags.length > 0 && (
                <div style={{ marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {clause.attention_flags.map((flag, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '6px 10px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'rgba(245, 158, 11, 0.1)',
                        border: '1px solid rgba(245, 158, 11, 0.25)',
                        fontSize: '0.8rem',
                        color: '#fde68a',
                      }}
                    >
                      <AlertTriangle size={15} />
                      <span><strong>{flag.category}:</strong> {flag.reason}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Citations */}
              <div style={{ marginTop: '8px' }}>
                {clause.citations.map((cite, idx) => (
                  <CitationBadge key={idx} citation={cite} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Structured Obligations Section */}
      {obligations.length > 0 && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '6px' }}>Extracted Obligations</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '16px' }}>
            Structured duties indicating actor, requirement, and consequence of non-performance.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
            {obligations.map((obl) => (
              <div key={obl.obligation_id} style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8', marginBottom: '4px' }}>
                  ACTOR: {obl.actor}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)', marginBottom: '8px' }}>
                  {obl.object}
                </div>
                {obl.deadline && (
                  <div style={{ fontSize: '0.75rem', color: '#fde68a' }}>
                    Deadline: {obl.deadline}
                  </div>
                )}
                {obl.source && <CitationBadge citation={obl.source} />}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
