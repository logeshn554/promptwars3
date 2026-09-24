import React, { useRef, useState } from 'react';
import { UploadCloud, File, Trash2, CheckCircle2, AlertCircle } from 'lucide-react';
import { DocumentMetadata } from '../types/legal';

interface DocumentManagerProps {
  documents: DocumentMetadata[];
  selectedDocId: string | null;
  onSelectDoc: (id: string) => void;
  onUpload: (file: File) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  loading: boolean;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({
  documents,
  selectedDocId,
  onSelectDoc,
  onUpload,
  onDelete,
  loading,
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    setErrorMsg(null);

    // Validate size (< 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setErrorMsg('File size exceeds the 10MB maximum limit.');
      return;
    }

    try {
      await onUpload(file);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Upload failed');
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
      {/* Upload Zone */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <UploadCloud size={20} color="#60a5fa" />
          Upload Legal Document
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>
          Upload PDF, DOCX, or TXT agreements. Analyzed strictly with structure-aware chunking and citation metadata preservation.
        </p>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFiles(e.dataTransfer.files);
          }}
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          aria-label="Upload document drag and drop area"
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click(); }}
          style={{
            border: dragOver ? '2px dashed #60a5fa' : '2px dashed var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '36px 20px',
            textAlign: 'center',
            cursor: 'pointer',
            background: dragOver ? 'rgba(59, 130, 246, 0.08)' : 'rgba(255, 255, 255, 0.02)',
            transition: 'all 0.2s ease',
          }}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => handleFiles(e.target.files)}
            accept=".pdf,.docx,.txt"
            style={{ display: 'none' }}
          />
          <UploadCloud size={40} color="#9ca3af" style={{ margin: '0 auto 12px' }} />
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            {loading ? 'Uploading and analyzing document...' : 'Click to upload or drag & drop'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Supported formats: PDF, DOCX, TXT (Max 10 MB)
          </div>
        </div>

        {errorMsg && (
          <div style={{ marginTop: '14px', padding: '10px 14px', borderRadius: 'var(--radius-md)', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#fda4af', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Ingested Documents List */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <File size={20} color="#c084fc" />
          Ingested Documents ({documents.length})
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '16px' }}>
          Select an active document to view clause analysis, ask grounded questions, or compare versions.
        </p>

        {documents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            No documents uploaded yet. Upload an agreement to begin.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '380px', overflowY: 'auto' }}>
            {documents.map((doc) => {
              const isSelected = selectedDocId === doc.document_id;
              return (
                <div
                  key={doc.document_id}
                  onClick={() => onSelectDoc(doc.document_id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    borderRadius: 'var(--radius-md)',
                    background: isSelected ? 'rgba(59, 130, 246, 0.15)' : 'var(--bg-secondary)',
                    border: isSelected ? '1px solid #3b82f6' : '1px solid var(--border-subtle)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
                    <div style={{ color: isSelected ? '#60a5fa' : 'var(--text-muted)' }}>
                      <File size={20} />
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontSize: '0.9rem', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {doc.filename}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        {doc.file_type.toUpperCase()} • {(doc.file_size_bytes / 1024).toFixed(1)} KB • {doc.page_count} page{doc.page_count > 1 ? 's' : ''}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {isSelected && (
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#34d399', fontSize: '0.75rem', fontWeight: 600 }}>
                        <CheckCircle2 size={14} /> Active
                      </span>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(doc.document_id);
                      }}
                      title="Delete document"
                      aria-label={`Delete ${doc.filename}`}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '6px',
                        borderRadius: '4px',
                      }}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
