import React from 'react';
import { ProvenanceCitation } from '../types/legal';
import { Bookmark } from 'lucide-react';

interface CitationBadgeProps {
  citation: ProvenanceCitation;
  onClick?: () => void;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({ citation, onClick }) => {
  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
      aria-label={`Citation for page ${citation.page_number || 1}, clause ${citation.clause_number || 'General'}`}
      style={{
        display: 'inline-flex',
        flexDirection: 'column',
        gap: '4px',
        padding: '8px 12px',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(59, 130, 246, 0.08)',
        border: '1px solid rgba(59, 130, 246, 0.25)',
        cursor: onClick ? 'pointer' : 'default',
        fontSize: '0.8rem',
        margin: '4px 0',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#93c5fd', fontWeight: 600 }}>
        <Bookmark size={14} />
        <span>
          {citation.document_name} • Page {citation.page_number || 1}
          {citation.clause_number && ` • Clause ${citation.clause_number}`}
        </span>
      </div>
      {citation.excerpt && (
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontStyle: 'italic', borderLeft: '2px solid var(--accent-blue)', paddingLeft: '8px' }}>
          "{citation.excerpt}"
        </p>
      )}
    </div>
  );
};
