import CaseSummaryCard from '../components/CaseSummaryCard';

export default {
  title: 'Nyaya UI Kit/Case Presentation/CaseSummaryCard',
  component: CaseSummaryCard,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export const Default = {
  args: {
    caseId: 'CASE-2024-001',
    title: 'Property Dispute Resolution',
    overview: 'A dispute between neighboring property owners regarding boundary lines and easement rights.',
    keyFacts: [
      'Property boundary dispute since 2022',
      'Involves 2-acre land parcel',
      'Previous mediation attempts failed',
      'Court filing in District Court'
    ],
    jurisdiction: 'India - Karnataka',
    confidence: 0.85,
    summaryAnalysis: 'High likelihood of settlement through mediation. Recommended to gather additional survey documents.',
    dateFiled: '2024-01-15',
    status: 'Active',
    parties: ['Plaintiff: Mr. Rajesh Kumar', 'Defendant: Ms. Priya Sharma']
  },
};

export const LowConfidence = {
  args: {
    ...Default.args,
    confidence: 0.45,
    summaryAnalysis: 'Limited information available. Additional legal research recommended.',
  },
};

export const DataError = {
  args: {
    title: null, // Missing required data
    overview: 'Some overview',
    keyFacts: ['fact1'],
    jurisdiction: 'India',
    confidence: 0.8,
    summaryAnalysis: 'Analysis here'
  },
};