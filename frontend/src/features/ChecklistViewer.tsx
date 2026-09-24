import React, { useState } from 'react';
import { ChecklistItem } from '../types/legal';
import { CheckSquare, Square, RefreshCw } from 'lucide-react';
import { CitationBadge } from '../components/CitationBadge';

interface ChecklistViewerProps {
  items: ChecklistItem[];
  onRefresh: () => Promise<void>;
  loading: boolean;
}

export const ChecklistViewer: React.FC<ChecklistViewerProps> = ({
  items,
  onRefresh,
  loading,
}) => {
  const [checklist, setChecklist] = useState<ChecklistItem[]>(items);

  const toggleItem = (id: string) => {
    setChecklist((prev) =>
      prev.map((item) => (item.item_id === id ? { ...item, completed: !item.completed } : item))
    );
  };

  const completedCount = checklist.filter((i) => i.completed).length;
  const progressPercent = checklist.length > 0 ? Math.round((completedCount / checklist.length) * 100) : 0;

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckSquare size={20} color="#10b981" />
            Actionable Pre-Signing & Verification Checklist
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Grounded verification items linked directly to specific contract clauses.
          </p>
        </div>

        <button onClick={onRefresh} disabled={loading} className="btn-secondary" style={{ padding: '8px 14px' }}>
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          <span>Regenerate</span>
        </button>
      </div>

      {/* Progress Bar */}
      <div style={{ marginBottom: '20px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', padding: '12px 16px', border: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, marginBottom: '6px' }}>
          <span>Completion Progress ({completedCount}/{checklist.length})</span>
          <span>{progressPercent}%</span>
        </div>
        <div style={{ height: '8px', background: 'var(--bg-tertiary)', borderRadius: '9999px', overflow: 'hidden' }}>
          <div style={{ width: `${progressPercent}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #06b6d4)', transition: 'width 0.3s ease' }} />
        </div>
      </div>

      {/* Checklist items */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {checklist.map((item) => (
          <div
            key={item.item_id}
            onClick={() => toggleItem(item.item_id)}
            role="checkbox"
            aria-checked={item.completed}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleItem(item.item_id);
              }
            }}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              padding: '14px 16px',
              borderRadius: 'var(--radius-md)',
              background: item.completed ? 'rgba(16, 185, 129, 0.06)' : 'var(--bg-secondary)',
              border: item.completed ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid var(--border-subtle)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ color: item.completed ? '#10b981' : 'var(--text-muted)', marginTop: '2px' }}>
              {item.completed ? <CheckSquare size={18} /> : <Square size={18} />}
            </div>

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                <span className="badge badge-info">{item.category}</span>
                {item.source_clause && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Linked to: {item.source_clause}
                  </span>
                )}
              </div>
              <p style={{ fontSize: '0.9rem', color: item.completed ? 'var(--text-secondary)' : 'var(--text-primary)', textDecoration: item.completed ? 'line-through' : 'none' }}>
                {item.task}
              </p>
              {item.citation && <CitationBadge citation={item.citation} />}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
