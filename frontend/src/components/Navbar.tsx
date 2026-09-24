import React from 'react';
import { Scale, ShieldCheck, FileText, ArrowRightLeft, CheckSquare, HelpCircle, Info } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  documentCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, documentCount }) => {
  const navItems = [
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'analysis', label: 'Analysis & Clauses', icon: Scale },
    { id: 'qa', label: 'Ask Document', icon: HelpCircle },
    { id: 'compare', label: 'Compare Versions', icon: ArrowRightLeft },
    { id: 'checklist', label: 'Checklist', icon: CheckSquare },
    { id: 'lawyer', label: 'Lawyer Prep', icon: ShieldCheck },
    { id: 'about', label: 'About & Disclaimer', icon: Info },
  ];

  return (
    <header style={{ borderBottom: '1px solid var(--border-subtle)', background: 'rgba(11, 15, 25, 0.9)', backdropFilter: 'blur(10px)', position: 'sticky', top: 0, zIndex: 50 }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '14px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'linear-gradient(135deg, #3b82f6, #6366f1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', boxShadow: '0 2px 8px rgba(59, 130, 246, 0.4)' }}>
            <Scale size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em', background: 'linear-gradient(to right, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                NyayaLens
              </span>
              <span style={{ fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px', background: 'rgba(59, 130, 246, 0.2)', color: '#93c5fd', fontWeight: 600 }}>
                v1.0
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Explain. Cite. Verify. Never pretend to be the lawyer.</p>
          </div>
        </div>

        <nav aria-label="Main Navigation" style={{ display: 'flex', gap: '6px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  borderRadius: 'var(--radius-md)',
                  border: isActive ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid transparent',
                  background: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                  color: isActive ? '#93c5fd' : 'var(--text-secondary)',
                  fontSize: '0.85rem',
                  fontWeight: isActive ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <Icon size={16} />
                <span>{item.label}</span>
                {item.id === 'documents' && documentCount > 0 && (
                  <span style={{ fontSize: '0.7rem', padding: '1px 5px', borderRadius: '9999px', background: 'var(--bg-tertiary)', color: '#fff' }}>
                    {documentCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
