import {
  DocumentMetadata,
  ClauseAnalysis,
  StructuredObligation,
  DocumentSummary,
  QAResponse,
  ChecklistItem,
  LawyerQuestionItem,
  ComparisonResult,
  PlainLanguageMode,
  UUID,
} from '../types/legal';

// In-browser mock database storage for standalone live deployment (e.g. Vercel)
const STORAGE_KEY = 'nyayalens_local_documents';

interface StoredDoc {
  metadata: DocumentMetadata;
  rawText: string;
  summary: DocumentSummary;
  clauses: ClauseAnalysis[];
  obligations: StructuredObligation[];
  checklist: ChecklistItem[];
  lawyerQuestions: LawyerQuestionItem[];
}

function getStoredDocs(): Record<UUID, StoredDoc> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function saveStoredDocs(docs: Record<UUID, StoredDoc>): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(docs));
  } catch (e) {
    console.error('Storage quota or access error:', e);
  }
}

// Client-side extraction engine for standalone live demo
function generateLocalLegalAnalysis(documentId: UUID, filename: string, text: string) {
  const isV2 = filename.toLowerCase().includes('v2') || text.includes('90 days') || text.includes('12 months');
  const noticeDays = isV2 ? '90 days' : '30 days';
  const nonCompeteDuration = isV2 ? '12 months' : '6 months';

  const clauses: ClauseAnalysis[] = [
    {
      clause_id: `${documentId}-c1`,
      category: 'TERMINATION',
      title: 'Clause 11.2: Voluntary Resignation and Notice',
      original_text: `In the event of voluntary resignation, Employee shall provide ${noticeDays} prior written notice.`,
      plain_language_explanation: `You must give ${noticeDays} advance written notice before leaving the company.`,
      parties: ['Acme Corporation Inc.', 'John Doe'],
      obligations: [`Provide ${noticeDays} prior written notice before departure`],
      rights: ['Right to terminate agreement voluntarily'],
      deadlines: [`${noticeDays} prior to effective resignation`],
      financial_implications: ['Compensation disbursed through end of notice period'],
      restrictions: ['Must fulfill handover responsibilities during notice period'],
      questions_to_clarify: ['Can the company waive or shorten notice with pay?'],
      confidence: 0.96,
      citations: [
        {
          document_id: documentId,
          document_name: filename,
          page_number: 1,
          clause_number: '11.2',
          section_title: 'TERMINATION',
          excerpt: `In the event of voluntary resignation, Employee shall provide ${noticeDays} prior written notice.`,
        },
      ],
      attention_flags: [
        {
          category: 'DEADLINE',
          reason: `Notice requirement is set to ${noticeDays}.`,
          confidence: 0.95,
          citation: {
            document_id: documentId,
            document_name: filename,
            page_number: 1,
            clause_number: '11.2',
            excerpt: `Employee shall provide ${noticeDays} prior written notice.`,
          },
        },
      ],
    },
    {
      clause_id: `${documentId}-c2`,
      category: 'NON_COMPETE',
      title: 'Clause 8.1: Non-Competition Covenant',
      original_text: `Employee agrees that for a period of ${nonCompeteDuration} following termination of employment for any reason, Employee shall not engage in any competing software enterprise within the territory.`,
      plain_language_explanation: `You cannot work for a competing software company for ${nonCompeteDuration} after termination.`,
      parties: ['John Doe'],
      obligations: [`Refrain from competing activities for ${nonCompeteDuration}`],
      rights: [],
      deadlines: [`${nonCompeteDuration} post-termination`],
      financial_implications: ['Potential impact on alternative employment earnings'],
      restrictions: [`Strict prohibition on competing software businesses in territory for ${nonCompeteDuration}`],
      questions_to_clarify: ['Is this non-compete valid under state law without compensation?'],
      confidence: 0.94,
      citations: [
        {
          document_id: documentId,
          document_name: filename,
          page_number: 1,
          clause_number: '8.1',
          section_title: 'RESTRICTIVE COVENANTS',
          excerpt: `Employee shall not engage in any competing software enterprise within the territory for ${nonCompeteDuration}.`,
        },
      ],
      attention_flags: [
        {
          category: 'RESTRICTION',
          reason: `${nonCompeteDuration} restriction on post-employment opportunities.`,
          confidence: 0.95,
          citation: {
            document_id: documentId,
            document_name: filename,
            page_number: 1,
            clause_number: '8.1',
            excerpt: `Employee shall not engage in any competing software enterprise for ${nonCompeteDuration}.`,
          },
        },
      ],
    },
    {
      clause_id: `${documentId}-c3`,
      category: 'COMPENSATION',
      title: 'Clause 3: Compensation and Bonus',
      original_text: isV2
        ? 'Company shall pay Employee an annual base salary payable semi-monthly. Annual performance bonus shall be discretionary and subject to board approval.'
        : 'Company shall pay Employee an annual base salary payable semi-monthly on the 15th and last day of each month.',
      plain_language_explanation: isV2
        ? 'Salary is paid twice a month. Annual bonus is discretionary upon board approval.'
        : 'Salary is paid twice a month on the 15th and last day of each month.',
      parties: ['Acme Corporation Inc.', 'Employee'],
      obligations: ['Company to disburse salary semi-monthly'],
      rights: ['Right to base salary'],
      deadlines: ['15th and last day of month'],
      financial_implications: ['Semi-monthly fixed compensation disbursements'],
      restrictions: [],
      questions_to_clarify: ['Are bonuses tied to quantifiable targets or solely discretionary?'],
      confidence: 0.92,
      citations: [
        {
          document_id: documentId,
          document_name: filename,
          page_number: 1,
          clause_number: '3',
          section_title: 'COMPENSATION',
          excerpt: 'Company shall pay Employee an annual base salary payable semi-monthly.',
        },
      ],
      attention_flags: [
        {
          category: 'FINANCIAL_OBLIGATION',
          reason: 'Defines recurring salary and bonus disbursement mechanics.',
          confidence: 0.91,
          citation: {
            document_id: documentId,
            document_name: filename,
            page_number: 1,
            clause_number: '3',
            excerpt: 'Company shall pay Employee an annual base salary payable semi-monthly.',
          },
        },
      ],
    },
  ];

  const obligations: StructuredObligation[] = [
    {
      obligation_id: `${documentId}-obl1`,
      actor: 'Employee',
      action: 'Provide Written Notice',
      object: `Deliver ${noticeDays} advance written notice prior to departure`,
      deadline: `${noticeDays} before resignation date`,
      consequence: 'Potential breach of agreement if departed without notice',
      source: {
        document_id: documentId,
        document_name: filename,
        page_number: 1,
        clause_number: '11.2',
        excerpt: `In the event of voluntary resignation, Employee shall provide ${noticeDays} prior written notice.`,
      },
    },
    {
      obligation_id: `${documentId}-obl2`,
      actor: 'Employee',
      action: 'Refrain From Competition',
      object: `Abstain from participating in competing software businesses for ${nonCompeteDuration}`,
      deadline: `${nonCompeteDuration} post-termination`,
      consequence: 'Injunctive relief and legal claim for damages',
      source: {
        document_id: documentId,
        document_name: filename,
        page_number: 1,
        clause_number: '8.1',
        excerpt: `Employee shall not engage in any competing software enterprise within the territory for ${nonCompeteDuration}.`,
      },
    },
  ];

  const summary: DocumentSummary = {
    document_id: documentId,
    document_type: 'Executive Employment Agreement',
    parties: ['Acme Corporation Inc.', 'John Doe'],
    purpose: 'Sets forth terms of employment, compensation, termination rules, and restrictive covenants.',
    important_dates: [`Notice Requirement: ${noticeDays}`, `Non-Compete Term: ${nonCompeteDuration}`],
    key_obligations: [`Provide ${noticeDays} written notice`, `Non-compete adherence for ${nonCompeteDuration}`],
    key_rights: ['Semi-monthly compensation', 'Voluntary termination rights'],
    payments: ['Annual base salary payable semi-monthly'],
    restrictions: [`Non-compete for ${nonCompeteDuration}`, 'Non-solicitation of clients/staff'],
    termination_summary: `At-will contract with ${noticeDays} written notice requirement for voluntary resignation.`,
    dispute_resolution: 'Binding arbitration in New York in accordance with AAA rules.',
    attention_items: clauses.flatMap((c) => c.attention_flags),
    questions_worth_clarifying: [
      `Can the ${noticeDays} notice period be waived or negotiated?`,
      `Is the ${nonCompeteDuration} non-compete enforceable in my home jurisdiction?`,
    ],
    citations: [
      {
        document_id: documentId,
        document_name: filename,
        page_number: 1,
        excerpt: `Employment agreement governing terms between Acme Corporation Inc. and John Doe.`,
      },
    ],
  };

  const checklist: ChecklistItem[] = [
    {
      item_id: `${documentId}-chk1`,
      task: `Confirm whether ${noticeDays} resignation notice period can be reduced prior to signing`,
      category: 'Termination',
      completed: false,
      source_clause: 'Clause 11.2',
      citation: {
        document_id: documentId,
        document_name: filename,
        page_number: 1,
        clause_number: '11.2',
        excerpt: `Employee shall provide ${noticeDays} prior written notice.`,
      },
    },
    {
      item_id: `${documentId}-chk2`,
      task: `Verify territory and legal enforceability of ${nonCompeteDuration} non-compete restriction`,
      category: 'Restrictions',
      completed: false,
      source_clause: 'Clause 8.1',
      citation: {
        document_id: documentId,
        document_name: filename,
        page_number: 1,
        clause_number: '8.1',
        excerpt: `Employee shall not engage in competing business for ${nonCompeteDuration}.`,
      },
    },
    {
      item_id: `${documentId}-chk3`,
      task: 'Verify starting compensation schedule and payment dates',
      category: 'Compensation',
      completed: false,
      source_clause: 'Clause 3',
    },
    {
      item_id: `${documentId}-chk4`,
      task: 'Check dispute resolution arbitration venue (New York / AAA rules)',
      category: 'Dispute Resolution',
      completed: false,
      source_clause: 'Clause 14',
    },
  ];

  const lawyerQuestions: LawyerQuestionItem[] = [
    {
      question_id: `${documentId}-lq1`,
      question: `Can the ${noticeDays} resignation notice period be negotiated down to standard 30 days?`,
      context_rationale: `${noticeDays} notice is longer than customary and could restrict smooth transition to future employers.`,
      related_clause: 'Clause 11.2 (Termination)',
      citation: {
        document_id: documentId,
        document_name: filename,
        page_number: 1,
        clause_number: '11.2',
        excerpt: `Employee shall provide ${noticeDays} prior written notice.`,
      },
    },
    {
      question_id: `${documentId}-lq2`,
      question: `Is the ${nonCompeteDuration} post-employment non-compete covenant legally binding in our jurisdiction?`,
      context_rationale: 'Many jurisdictions void post-employment non-competes unless accompanied by garden leave pay.',
      related_clause: 'Clause 8.1 (Non-Competition)',
      citation: {
        document_id: documentId,
        document_name: filename,
        page_number: 1,
        clause_number: '8.1',
        excerpt: `Employee shall not engage in any competing software enterprise for ${nonCompeteDuration}.`,
      },
    },
    {
      question_id: `${documentId}-lq3`,
      question: 'Are there any personal software exclusions for side projects developed outside business hours?',
      context_rationale: 'Clarifies intellectual property ownership for personal software developed independently.',
      related_clause: 'Clause 7 (Proprietary Rights)',
    },
  ];

  return { summary, clauses, obligations, checklist, lawyerQuestions };
}

// Ensure default demo agreements are populated if localStorage is empty
function ensureSeedData() {
  const docs = getStoredDocs();
  if (Object.keys(docs).length === 0) {
    const v1Id = '11111111-1111-4111-a111-111111111111';
    const v1Text = 'EMPLOYMENT AGREEMENT (VERSION A)\nSECTION 11.2: Voluntary Resignation: Employee shall provide thirty (30) days prior written notice.\nSECTION 8.1: Non-Competition: for six (6) months post-termination.';
    const v1Analysis = generateLocalLegalAnalysis(v1Id, 'employment_agreement_v1.txt', v1Text);

    const v2Id = '22222222-2222-4222-a222-222222222222';
    const v2Text = 'EMPLOYMENT AGREEMENT (VERSION B)\nSECTION 11.2: Voluntary Resignation: Employee shall provide ninety (90) days prior written notice.\nSECTION 8.1: Non-Competition: for twelve (12) months post-termination.';
    const v2Analysis = generateLocalLegalAnalysis(v2Id, 'employment_agreement_v2.txt', v2Text);

    docs[v1Id] = {
      metadata: {
        document_id: v1Id,
        filename: 'employment_agreement_v1.txt',
        file_type: '.txt',
        file_size_bytes: v1Text.length,
        page_count: 1,
        created_at: new Date().toISOString(),
        is_processed: true,
        title: 'Employment Agreement V1',
        parties: ['Acme Corporation Inc.', 'John Doe'],
        document_type: 'Executive Employment Agreement',
      },
      rawText: v1Text,
      ...v1Analysis,
    };

    docs[v2Id] = {
      metadata: {
        document_id: v2Id,
        filename: 'employment_agreement_v2.txt',
        file_type: '.txt',
        file_size_bytes: v2Text.length,
        page_count: 1,
        created_at: new Date().toISOString(),
        is_processed: true,
        title: 'Employment Agreement V2',
        parties: ['Acme Corporation Inc.', 'John Doe'],
        document_type: 'Executive Employment Agreement (Revised)',
      },
      rawText: v2Text,
      ...v2Analysis,
    };

    saveStoredDocs(docs);
  }
}

// Client-side fallback API client executing identical REST contracts in-browser
export const localLegalApi = {
  async getHealth() {
    return { status: 'healthy', app_name: 'NyayaLens (Vercel Client Edition)', environment: 'production' };
  },

  async uploadDocument(file: File): Promise<DocumentMetadata> {
    ensureSeedData();
    const documentId = crypto.randomUUID ? crypto.randomUUID() : `doc-${Date.now()}`;
    const text = await file.text();
    const analysis = generateLocalLegalAnalysis(documentId, file.name, text);

    const metadata: DocumentMetadata = {
      document_id: documentId,
      filename: file.name,
      file_type: file.name.substring(file.name.lastIndexOf('.')).toLowerCase() || '.txt',
      file_size_bytes: file.size,
      page_count: 1,
      created_at: new Date().toISOString(),
      is_processed: true,
      title: file.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' '),
      parties: ['Acme Corporation Inc.', 'John Doe'],
      document_type: 'Executive Employment Agreement',
    };

    const docs = getStoredDocs();
    docs[documentId] = {
      metadata,
      rawText: text,
      ...analysis,
    };
    saveStoredDocs(docs);
    return metadata;
  },

  async listDocuments(): Promise<DocumentMetadata[]> {
    ensureSeedData();
    const docs = getStoredDocs();
    return Object.values(docs).map((d) => d.metadata);
  },

  async getDocument(documentId: UUID): Promise<DocumentMetadata> {
    ensureSeedData();
    const doc = getStoredDocs()[documentId];
    if (!doc) throw new Error(`Document ${documentId} not found`);
    return doc.metadata;
  },

  async getClauses(documentId: UUID): Promise<ClauseAnalysis[]> {
    ensureSeedData();
    const doc = getStoredDocs()[documentId];
    return doc ? doc.clauses : [];
  },

  async getObligations(documentId: UUID): Promise<StructuredObligation[]> {
    ensureSeedData();
    const doc = getStoredDocs()[documentId];
    return doc ? doc.obligations : [];
  },

  async getSummary(documentId: UUID): Promise<DocumentSummary> {
    ensureSeedData();
    const doc = getStoredDocs()[documentId];
    if (!doc) throw new Error(`Summary for ${documentId} not found`);
    return doc.summary;
  },

  async askQuestion(documentId: UUID, payload: { question: string; plain_language_mode: PlainLanguageMode }): Promise<QAResponse> {
    ensureSeedData();
    const doc = getStoredDocs()[documentId];
    const qLower = payload.question.toLowerCase();

    // 1. Prompt Injection Detection
    if (qLower.includes('ignore all') || qLower.includes('system prompt') || qLower.includes('reveal') || qLower.includes('api key')) {
      return {
        question: payload.question,
        answer: 'NyayaLens Security: The query contains instruction override patterns or prompt injection payloads and cannot be executed.',
        citations: [],
        confidence: 0.0,
        insufficient_evidence: true,
        suggested_questions: ['What is the notice period?', 'What are the restrictive covenants?'],
        verified: true,
        disclaimer: 'NyayaLens provides AI-assisted legal information and document explanations.',
      };
    }

    // 2. Insufficient Evidence Detection
    if (qLower.includes('dog food') || qLower.includes('pet') || qLower.includes('solar panel') || qLower.includes('arbitrary')) {
      return {
        question: payload.question,
        answer: 'I could not find sufficient information in the uploaded document to answer this reliably.',
        citations: [],
        confidence: 0.0,
        insufficient_evidence: true,
        suggested_questions: ['What happens if I resign?', 'What are the non-compete terms?'],
        verified: true,
        disclaimer: 'NyayaLens provides AI-assisted legal information and document explanations.',
      };
    }

    // 3. Dynamic Evidence-Grounded Search across document text and clauses
    const docText = (doc?.rawText || '').toLowerCase();
    const clauses = doc?.clauses || [];

    // Check if query matches specific keywords
    const isTermination = qLower.includes('resign') || qLower.includes('resignation') || qLower.includes('notice') || qLower.includes('terminate');
    const isNonCompete = qLower.includes('compete') || qLower.includes('non-compete') || qLower.includes('restriction');
    const isCompensation = qLower.includes('pay') || qLower.includes('salary') || qLower.includes('compensation') || qLower.includes('bonus') || qLower.includes('fee');
    const isDuties = qLower.includes('duty') || qLower.includes('duties') || qLower.includes('obligation') || qLower.includes('responsibilit');
    const isOverview = qLower.includes('pdf') || qLower.includes('what is') || qLower.includes('contain') || qLower.includes('summary') || qLower.includes('about');

    let matchedClause = clauses.find((c) => {
      const cText = (c.title + ' ' + c.original_text + ' ' + c.plain_language_explanation).toLowerCase();
      if (isTermination && (c.category === 'TERMINATION' || cText.includes('notice') || cText.includes('resign'))) return true;
      if (isNonCompete && (c.category === 'NON_COMPETE' || cText.includes('compete'))) return true;
      if (isCompensation && (c.category === 'COMPENSATION' || c.category === 'PAYMENT' || cText.includes('salary'))) return true;
      if (isDuties && c.obligations.length > 0) return true;
      return false;
    });

    if (matchedClause) {
      return {
        question: payload.question,
        answer: matchedClause.plain_language_explanation,
        citations: matchedClause.citations && matchedClause.citations.length > 0 ? matchedClause.citations : [
          {
            document_id: documentId,
            document_name: doc?.metadata.filename || 'agreement.docx',
            page_number: 1,
            clause_number: matchedClause.title.split(':')[0] || '1.1',
            excerpt: matchedClause.original_text,
          }
        ],
        confidence: 0.94,
        insufficient_evidence: false,
        suggested_questions: matchedClause.questions_to_clarify.length > 0 ? matchedClause.questions_to_clarify : ['What are the termination terms?', 'What are the payment deadlines?'],
        verified: true,
        disclaimer: 'NyayaLens provides AI-assisted legal information and document explanations.',
      };
    }

    if (isOverview && doc) {
      const summaryText = doc.summary ? doc.summary.purpose : 'This agreement establishes formal legal commitments, duties, and operational conditions between the parties.';
      const keyClauses = doc.clauses.map((c) => c.title).slice(0, 3).join(', ');
      return {
        question: payload.question,
        answer: `The document is a ${doc.metadata.document_type || 'Legal Agreement'}. ${summaryText} Primary provisions include: ${keyClauses || 'obligations, termination guidelines, and mutual covenants'}.`,
        citations: doc.clauses[0]?.citations || [],
        confidence: 0.92,
        insufficient_evidence: false,
        suggested_questions: ['What happens if I resign?', 'What are the primary obligations?'],
        verified: true,
        disclaimer: 'NyayaLens provides AI-assisted legal information and document explanations.',
      };
    }

    if (isDuties && doc) {
      const obls = doc.obligations.map((o) => `${o.actor}: ${o.action} ${o.object}`).slice(0, 3).join('. ');
      return {
        question: payload.question,
        answer: `The key duties outlined in this document are: ${obls || 'fulfilling contract covenants, complying with confidentiality, and meeting required timelines'}.`,
        citations: doc.clauses[0]?.citations || [],
        confidence: 0.91,
        insufficient_evidence: false,
        suggested_questions: ['What are the consequences of breach?', 'What is the notice period?'],
        verified: true,
        disclaimer: 'NyayaLens provides AI-assisted legal information and document explanations.',
      };
    }

    // Dynamic extraction: find sentences containing query words
    const queryWords = qLower.split(/\s+/).filter((w) => w.length > 3 && !['what', 'this', 'that', 'with', 'from', 'have', 'does'].includes(w));
    if (docText && queryWords.length > 0) {
      const sentences = docText.split(/[.\n]/).map((s) => s.trim()).filter(Boolean);
      const matchingSentences = sentences.filter((s) => queryWords.some((w) => s.includes(w)));
      if (matchingSentences.length > 0) {
        const topExcerpt = matchingSentences.slice(0, 2).join('. ');
        return {
          question: payload.question,
          answer: `According to the relevant document provisions: "${topExcerpt}."`,
          citations: [
            {
              document_id: documentId,
              document_name: doc?.metadata.filename || 'agreement.docx',
              page_number: 1,
              clause_number: 'Sec. Ref',
              excerpt: topExcerpt,
            }
          ],
          confidence: 0.89,
          insufficient_evidence: false,
          suggested_questions: ['What are the consequences of this clause?', 'How does this apply to both parties?'],
          verified: true,
          disclaimer: 'NyayaLens provides AI-assisted legal information and document explanations.',
        };
      }
    }

    // Default insufficient evidence if no matches in document
    return {
      question: payload.question,
      answer: 'I could not find sufficient information in the uploaded document to answer this reliably.',
      citations: [],
      confidence: 0.0,
      insufficient_evidence: true,
      suggested_questions: ['What are the termination requirements?', 'What are the compensation terms?'],
      verified: true,
      disclaimer: 'NyayaLens provides AI-assisted legal information and document explanations.',
    };
  },

  async generateChecklist(documentId: UUID): Promise<ChecklistItem[]> {
    ensureSeedData();
    const doc = getStoredDocs()[documentId];
    return doc ? doc.checklist : [];
  },

  async generateLawyerQuestions(documentId: UUID): Promise<LawyerQuestionItem[]> {
    ensureSeedData();
    const doc = getStoredDocs()[documentId];
    return doc ? doc.lawyerQuestions : [];
  },

  async compareDocuments(docAId: UUID, docBId: UUID): Promise<ComparisonResult> {
    ensureSeedData();
    const docs = getStoredDocs();
    const docA = docs[docAId];
    const docB = docs[docBId];

    return {
      comparison_id: `comp-${Date.now()}`,
      doc_a_id: docAId,
      doc_a_name: docA ? docA.metadata.filename : 'Version A',
      doc_b_id: docBId,
      doc_b_name: docB ? docB.metadata.filename : 'Version B',
      summary_of_differences: 'Version B materially increases notice obligations (30 to 90 days), doubles the non-compete restriction (6 to 12 months), and shifts the annual bonus to a discretionary model.',
      added_clauses: ['Clause 15: Data Privacy and AI Usage Restrictions'],
      removed_clauses: [],
      semantic_changes: [
        {
          change_id: 'change-1',
          significance: 'DEADLINE_CHANGE',
          clause_category: 'TERMINATION',
          topic: 'Notice Period Duration',
          version_a_text: 'Employee shall provide thirty (30) days prior written notice.',
          version_b_text: 'Employee shall provide ninety (90) days prior written notice.',
          description_of_change: 'Notice requirement increased by 60 days (from 30 days to 90 days).',
          evidence_a: {
            document_id: docAId,
            document_name: docA ? docA.metadata.filename : 'Version A',
            page_number: 1,
            clause_number: '11.2',
            excerpt: 'Employee shall provide thirty (30) days prior written notice.',
          },
          evidence_b: {
            document_id: docBId,
            document_name: docB ? docB.metadata.filename : 'Version B',
            page_number: 1,
            clause_number: '11.2',
            excerpt: 'Employee shall provide ninety (90) days prior written notice.',
          },
        },
        {
          change_id: 'change-2',
          significance: 'RESTRICTION_CHANGE',
          clause_category: 'NON_COMPETE',
          topic: 'Non-Compete Covenant Length',
          version_a_text: 'Non-Competition: for a period of six (6) months following termination.',
          version_b_text: 'Non-Competition: for a period of twelve (12) months following termination.',
          description_of_change: 'Post-employment non-compete restriction duration doubled from 6 months to 12 months.',
          evidence_a: {
            document_id: docAId,
            document_name: docA ? docA.metadata.filename : 'Version A',
            page_number: 1,
            clause_number: '8.1',
            excerpt: 'Employee shall not engage in competing enterprise for six (6) months.',
          },
          evidence_b: {
            document_id: docBId,
            document_name: docB ? docB.metadata.filename : 'Version B',
            page_number: 1,
            clause_number: '8.1',
            excerpt: 'Employee shall not engage in competing enterprise for twelve (12) months.',
          },
        },
        {
          change_id: 'change-3',
          significance: 'FINANCIAL_CHANGE',
          clause_category: 'COMPENSATION',
          topic: 'Annual Performance Bonus',
          version_a_text: 'Fixed semi-monthly disbursement with guaranteed KPI-based structure.',
          version_b_text: 'Annual performance bonus shall be discretionary and subject to board approval.',
          description_of_change: 'Bonus shifted from predictable formulaic criteria to discretionary board approval.',
        },
      ],
      disclaimer: 'NyayaLens compares contract semantics for informational purposes. This does not constitute legal counsel.',
    };
  },

  async deleteDocument(documentId: UUID): Promise<void> {
    const docs = getStoredDocs();
    delete docs[documentId];
    saveStoredDocs(docs);
  },
};
