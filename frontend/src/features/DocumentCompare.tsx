import React, { useState } from 'react';
import { DocumentMetadata, ComparisonResult } from '../types/legal';
import { ArrowRightLeft } from 'lucide-react';
import { CitationBadge } from '../components/CitationBadge';

interface DocumentCompareProps {
  documents: DocumentMetadata[];
  onCompare: (docAId: string, docBId: string) => Promise<ComparisonResult>;
}

export const DocumentCompare: React.FC<DocumentCompareProps> = ({
  documents,
  onCompare,
}) => {
  const [docAId, setDocAId] = useState<string>(documents[0]?.document_id || '');
  const [docBId, setDocBId] = useState<string>(documents[1]?.document_id || documents[0]?.document_id || '');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparisonResult | null>(null);

  const handleRunCompare = async () => {
    if (!docAId || !docBId || docAId === docBId || loading) return;
    setLoading(true);
    try {
      const res = await onCompare(docAId, docBId);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ArrowRightLeft size={20} color="#a855f7" />
          Semantic Document Version Comparison
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '18px' }}>
          Goes beyond raw text diffs to detect concrete semantic modifications in notice periods, deadlines, restrictions, and financial commitments.
        </p>

        {documents.length < 2 ? (
          <div style={{ padding: '16px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: 'var(--radius-md)', color: '#fde68a', fontSize: '0.85rem' }}>
            Please upload at least two document versions (e.g. Version A and Version B) to perform semantic comparison.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '16px', alignItems: 'flex-end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Base Version (Version A)
              </label>
              <select
                value={docAId}
                onChange={(e) => setDocAId(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '10px 14px',
                  fontSize: '0.85rem',
                }}
              >
                {documents.map((d) => (
                  <option key={d.document_id} value={d.document_id}>{d.filename}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Revised Version (Version B)
              </label>
              <select
                value={docBId}
                onChange={(e) => setDocBId(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '10px 14px',
                  fontSize: '0.85rem',
                }}
              >
                {documents.map((d) => (
                  <option key={d.document_id} value={d.document_id}>{d.filename}</option>
                ))}
              </select>
            </div>

            <button
              onClick={handleRunCompare}
              disabled={loading || docAId === docBId}
              className="btn-primary"
              style={{ height: '42px' }}
            >
              <ArrowRightLeft size={16} />
              <span>{loading ? 'Comparing...' : 'Compare Versions'}</span>
            </button>
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {result && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ marginBottom: '18px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f3f4f6' }}>Executive Comparison Summary</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.5 }}>
              {result.summary_of_differences}
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {result.semantic_changes.map((change) => (
              <div
                key={change.change_id}
                style={{
                  background: 'var(--bg-secondary)',
                  borderRadius: 'var(--radius-md)',
                  padding: '18px',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="badge badge-attention">{change.significance}</span>
                    <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f3f4f6' }}>{change.topic}</span>
                  </div>
                </div>

                <p style={{ fontSize: '0.85rem', color: '#93c5fd', marginBottom: '14px', fontWeight: 500 }}>
                  {change.description_of_change}
                </p>

                {/* Side-by-side clause version comparison */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '10px' }}>
                  <div style={{ background: 'rgba(0,0,0,0.3)', padding: '12px', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid #ef4444' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f87171', marginBottom: '4px' }}>
                      Version A ({result.doc_a_name})
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                      "{change.version_a_text}"
                    </p>
                  </div>

                  <div style={{ background: 'rgba(0,0,0,0.3)', padding: '12px', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid #10b981' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#34d399', marginBottom: '4px' }}>
                      Version B ({result.doc_b_name})
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                      "{change.version_b_text}"
                    </p>
                  </div>
                </div>

                {change.evidence_a && <CitationBadge citation={change.evidence_a} />}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
