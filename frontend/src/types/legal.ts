export type UUID = string;

export type ClauseCategory =
  | 'TERMINATION'
  | 'CONFIDENTIALITY'
  | 'INDEMNIFICATION'
  | 'LIABILITY'
  | 'LIMITATION_OF_LIABILITY'
  | 'INTELLECTUAL_PROPERTY'
  | 'NON_COMPETE'
  | 'NON_SOLICITATION'
  | 'ARBITRATION'
  | 'GOVERNING_LAW'
  | 'JURISDICTION'
  | 'PAYMENT'
  | 'COMPENSATION'
  | 'RENEWAL'
  | 'NOTICE'
  | 'WARRANTY'
  | 'DATA_PRIVACY'
  | 'DATA_USAGE'
  | 'PENALTY'
  | 'FORCE_MAJEURE'
  | 'ASSIGNMENT'
  | 'SEVERABILITY'
  | 'DISPUTE_RESOLUTION'
  | 'INSURANCE'
  | 'EXCLUSIVITY'
  | 'RIGHT'
  | 'OBLIGATION'
  | 'DEADLINE'
  | 'OTHER';

export type AttentionFlagCategory =
  | 'INFORMATIONAL'
  | 'REQUIRES_ATTENTION'
  | 'FINANCIAL_OBLIGATION'
  | 'RESTRICTION'
  | 'DEADLINE'
  | 'AMBIGUITY'
  | 'TERMINATION_RELATED';

export type PlainLanguageMode = 'simple' | 'standard' | 'detailed';

export type ChangeSignificance =
  | 'MINOR_TEXT_CHANGE'
  | 'OBLIGATION_CHANGE'
  | 'FINANCIAL_CHANGE'
  | 'DEADLINE_CHANGE'
  | 'RESTRICTION_CHANGE'
  | 'RIGHTS_CHANGE'
  | 'TERMINATION_CHANGE';

export interface ProvenanceCitation {
  document_id: UUID;
  document_name: string;
  page_number?: number;
  section_title?: string;
  clause_number?: string;
  excerpt: string;
}

export interface AttentionFlag {
  category: AttentionFlagCategory;
  reason: string;
  confidence: number;
  citation: ProvenanceCitation;
}

export interface ClauseAnalysis {
  clause_id: UUID;
  category: ClauseCategory;
  title: string;
  original_text: string;
  plain_language_explanation: string;
  parties: string[];
  obligations: string[];
  rights: string[];
  deadlines: string[];
  financial_implications: string[];
  restrictions: string[];
  questions_to_clarify: string[];
  confidence: number;
  citations: ProvenanceCitation[];
  attention_flags: AttentionFlag[];
}

export interface StructuredObligation {
  obligation_id: UUID;
  actor: string;
  action: string;
  object: string;
  deadline?: string;
  condition?: string;
  consequence?: string;
  source: ProvenanceCitation;
}

export interface DocumentMetadata {
  document_id: UUID;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  page_count: number;
  created_at: string;
  is_processed: boolean;
  title?: string;
  parties: string[];
  document_type: string;
}

export interface DocumentSummary {
  document_id: UUID;
  document_type: string;
  parties: string[];
  purpose: string;
  important_dates: string[];
  key_obligations: string[];
  key_rights: string[];
  payments: string[];
  restrictions: string[];
  termination_summary: string;
  dispute_resolution: string;
  attention_items: AttentionFlag[];
  questions_worth_clarifying: string[];
  citations: ProvenanceCitation[];
}

export interface QARequest {
  question: string;
  plain_language_mode: PlainLanguageMode;
  top_k?: number;
}

export interface QAResponse {
  question: string;
  answer: string;
  citations: ProvenanceCitation[];
  confidence: number;
  insufficient_evidence: boolean;
  suggested_questions: string[];
  verified: boolean;
  disclaimer: string;
}

export interface ChecklistItem {
  item_id: UUID;
  task: string;
  category: string;
  completed: boolean;
  source_clause?: string;
  citation?: ProvenanceCitation;
}

export interface LawyerQuestionItem {
  question_id: UUID;
  question: string;
  context_rationale: string;
  related_clause?: string;
  citation?: ProvenanceCitation;
}

export interface SemanticChange {
  change_id: UUID;
  significance: ChangeSignificance;
  clause_category: ClauseCategory;
  topic: string;
  version_a_text: string;
  version_b_text: string;
  description_of_change: string;
  evidence_a?: ProvenanceCitation;
  evidence_b?: ProvenanceCitation;
}

export interface ComparisonResult {
  comparison_id: UUID;
  doc_a_id: UUID;
  doc_a_name: string;
  doc_b_id: UUID;
  doc_b_name: string;
  added_clauses: string[];
  removed_clauses: string[];
  semantic_changes: SemanticChange[];
  summary_of_differences: string;
  disclaimer: string;
}
