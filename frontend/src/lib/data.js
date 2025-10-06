export const expectations = [
  {
    id: 'EXP-001',
    title: 'Streamline onboarding for enterprise customers',
    owner: 'Alex Johnson',
    status: 'Awaiting Review',
    priority: 'High',
    domain: 'Onboarding',
    version: '0.3.0',
    impact: 8.7,
    ice: { impact: 8, confidence: 7, ease: 5 },
    iceScore: 20,
    flags: ['Needs persona validation', 'Escalated from CS'],
    mosCow: 'Must',
    metrics: ['Time-to-value < 7 days', 'Churn risk < 5%'],
    conflicts: ['EXP-004'],
    tags: ['Customer Success', 'Workflow Automation'],
    linkedRequirements: ['REQ-101'],
    summary:
      'Customer onboarding is inconsistent between regions, leading to delays and escalations. We need a unified workflow with automation hooks.'
  },
  {
    id: 'EXP-002',
    title: 'Consolidate compliance evidence tracking',
    owner: 'Priya Patel',
    status: 'Clarification Needed',
    priority: 'Medium',
    domain: 'Compliance',
    version: '0.2.1',
    impact: 7.9,
    ice: { impact: 7, confidence: 6, ease: 4 },
    iceScore: 17,
    flags: ['Requires legal review'],
    mosCow: 'Should',
    metrics: ['Audit readiness score ≥ 90'],
    conflicts: [],
    tags: ['Compliance', 'Reporting'],
    linkedRequirements: ['REQ-205'],
    summary:
      'Auditors request evidence packages in multiple formats. We need a centralized repository with automated document assembly.'
  },
  {
    id: 'EXP-003',
    title: 'Improve NLQ search accuracy',
    owner: 'Chen Wei',
    status: 'Approved',
    priority: 'High',
    domain: 'Intelligence',
    version: '1.0.0',
    impact: 8.2,
    ice: { impact: 9, confidence: 8, ease: 6 },
    iceScore: 23,
    flags: ['Has linked CR'],
    mosCow: 'Must',
    metrics: ['Precision ≥ 0.78', 'Recall ≥ 0.74'],
    conflicts: [],
    tags: ['AI/ML', 'Search'],
    linkedRequirements: ['REQ-330'],
    summary:
      'Field teams need natural language search to retrieve historical requirements and change logs quickly during workshops.'
  },
  {
    id: 'EXP-004',
    title: 'Regional onboarding workflow variant',
    owner: 'Michael Green',
    status: 'Archived',
    priority: 'Low',
    domain: 'Onboarding',
    version: '0.9.4',
    impact: 5.1,
    ice: { impact: 5, confidence: 5, ease: 6 },
    iceScore: 16,
    flags: ['Conflict with EXP-001'],
    mosCow: 'Could',
    metrics: ['Time-to-value < 10 days'],
    conflicts: ['EXP-001'],
    tags: ['Legacy'],
    linkedRequirements: [],
    summary:
      'Legacy workflow proposal kept for reference. Superseded by enterprise onboarding initiative.'
  }
];

export const requirements = [
  {
    id: 'REQ-101',
    title: 'Unified onboarding workspace',
    status: 'DoR Ready',
    lastUpdated: '2025-10-03',
    version: '1.2.0',
    priority: 'High',
    assignee: 'Alex Johnson',
    progress: 68,
    source: 'Expectation EXP-001',
    relatedExpectations: ['EXP-001'],
    linkedChangeRequests: ['CR-12'],
    owner: 'Alex Johnson',
    readiness: ['3/3 AC defined', 'Blocking conflicts resolved', 'Success metrics confirmed'],
    metrics: [
      { name: 'Time-to-value', target: '< 7 days', source: 'AI Suggested' },
      { name: 'NPS uplift', target: '+12', source: 'Analyst Input' }
    ]
  },
  {
    id: 'REQ-205',
    title: 'Compliance evidence repository',
    status: 'Draft',
    lastUpdated: '2025-10-01',
    version: '0.7.0',
    priority: 'Medium',
    assignee: 'Priya Patel',
    progress: 32,
    source: 'Expectation EXP-002',
    relatedExpectations: ['EXP-002'],
    linkedChangeRequests: [],
    owner: 'Priya Patel',
    readiness: ['1/3 AC defined', 'Pending data classification rules'],
    metrics: [
      { name: 'Audit readiness score', target: '≥ 90', source: 'AI Suggested' },
      { name: 'Evidence assembly time', target: '< 15 min', source: 'Manual' }
    ]
  },
  {
    id: 'REQ-330',
    title: 'Semantic NLQ engine',
    status: 'Approved',
    lastUpdated: '2025-09-28',
    version: '2.0.1',
    priority: 'High',
    assignee: 'Chen Wei',
    progress: 92,
    source: 'Expectation EXP-003',
    relatedExpectations: ['EXP-003'],
    linkedChangeRequests: ['CR-29'],
    owner: 'Chen Wei',
    readiness: ['LLM conflict scan passed', 'ICE score recalculated'],
    metrics: [
      { name: 'Precision', target: '≥ 0.78', source: 'Model Eval' },
      { name: 'Recall', target: '≥ 0.74', source: 'Model Eval' }
    ]
  }
];

export const changeRequests = [
  {
    id: 'CR-12',
    title: 'Extend onboarding workspace to partner teams',
    status: 'Impact Analysis',
    submitted: '2025-10-02',
    owner: 'Maria Gomez',
    priority: 'High',
    linkedRequirements: ['REQ-101'],
    impact: 'High',
    analysisStatus: 'In progress',
    version: 'Proposed 1.3.0',
    decisions: [
      { role: 'Product Owner', decision: 'Pending', due: '2025-10-08' },
      { role: 'Engineering Lead', decision: 'Reviewing', due: '2025-10-07' }
    ],
    impactSummary:
      'Requires integration with partner CRM and additional success metrics for partner enablement. No blocking conflicts detected.'
  },
  {
    id: 'CR-29',
    title: 'Update NLQ model baseline',
    status: 'Approved',
    submitted: '2025-09-24',
    owner: 'Chen Wei',
    priority: 'Medium',
    linkedRequirements: ['REQ-330'],
    impact: 'Medium',
    analysisStatus: 'Complete',
    version: 'Proposed 2.1.0',
    decisions: [
      { role: 'Product Owner', decision: 'Approved', due: '2025-09-26' },
      { role: 'Compliance', decision: 'Approved', due: '2025-09-27' }
    ],
    impactSummary:
      'Model baseline upgrade increases accuracy by 6% with no additional infrastructure cost.'
  },
  {
    id: 'CR-44',
    title: 'Automate compliance evidence reminders',
    status: 'Draft',
    submitted: '2025-10-04',
    owner: 'Priya Patel',
    priority: 'Low',
    linkedRequirements: ['REQ-205'],
    impact: 'Low',
    analysisStatus: 'Not started',
    version: 'Proposed 0.8.0',
    decisions: [
      { role: 'Product Owner', decision: 'Pending', due: '2025-10-10' }
    ],
    impactSummary: 'Automated reminders for missing evidence packs with integration to compliance calendar.'
  }
];

export const metricDefinitions = [
  { id: 'M-001', name: 'Time-to-value', type: 'Duration', unit: 'days', description: 'Time from contract signature to first successful use case.' },
  { id: 'M-002', name: 'Audit readiness score', type: 'Score', unit: 'points', description: 'Composite compliance index calculated by the AI auditor.' },
  { id: 'M-003', name: 'Precision', type: 'Ratio', unit: '', description: 'Relevant matches / total returned.' },
  { id: 'M-004', name: 'Recall', type: 'Ratio', unit: '', description: 'Relevant matches retrieved / total relevant.' }
];

export const aiRecommendations = [
  {
    id: 'AI-1',
    title: 'Suggested DoR checklist update',
    description:
      'Add verification step for partner enablement collateral before moving onboarding workspace requirements to Approved.',
    status: 'New'
  },
  {
    id: 'AI-2',
    title: 'Potential duplicate expectation detected',
    description:
      'Expectation EXP-001 overlaps with archived expectation EXP-771 (Onboarding automation). Review deduplication report.',
    status: 'Investigate'
  }
];

export const chatHistory = [
  {
    role: 'system',
    content: 'You are the AI co-pilot for the requirements control tower.'
  },
  {
    role: 'user',
    content: 'Summarize onboarding expectations by impact and readiness.'
  },
  {
    role: 'assistant',
    content:
      'Two onboarding expectations with high impact. EXP-001 is awaiting review with ICE 6.7; EXP-002 requires clarification on compliance workflows.'
  }
];

export const activityLog = [
  {
    id: 'ACT-001',
    type: 'Expectation',
    action: 'Added expectation EXP-001',
    timestamp: '10:24 AM',
    author: 'Alex Johnson'
  },
  {
    id: 'ACT-002',
    type: 'Conversion',
    action: 'Converted EXP-001 → REQ-101',
    timestamp: 'Yesterday',
    author: 'AI Copilot'
  },
  {
    id: 'ACT-003',
    type: 'Change Request',
    action: 'Created CR-12 for REQ-101',
    timestamp: '2 days ago',
    author: 'Maria Gomez'
  },
  {
    id: 'ACT-004',
    type: 'Status',
    action: 'REQ-205 moved to Draft',
    timestamp: '2 days ago',
    author: 'Priya Patel'
  }
];

export const bottlenecks = [
  {
    id: 'BN-001',
    title: 'Overdue analysis',
    severity: 'Warning',
    description: 'CR-12 pending engineering sign-off for 4 days.',
    cta: { label: 'Go to CR-12', target: 'changeRequests', ref: 'CR-12' }
  },
  {
    id: 'BN-002',
    title: 'Long review pending',
    severity: 'Critical',
    description: 'Expectation EXP-002 waiting for compliance review > 7 days.',
    cta: { label: 'Open EXP-002', target: 'expectations', ref: 'EXP-002' }
  },
  {
    id: 'BN-003',
    title: 'High-impact CR unreviewed',
    severity: 'Warning',
    description: 'CR-44 not triaged; linked requirement at 32% progress.',
    cta: { label: 'Review CR-44', target: 'changeRequests', ref: 'CR-44' }
  }
];

export const projectMetrics = [
  {
    id: 'PM-1',
    title: 'Expectation to Requirement conversion',
    value: '62%',
    delta: '+5% WoW',
    trend: [48, 50, 52, 55, 57, 60, 62]
  },
  {
    id: 'PM-2',
    title: 'Average requirement cycle time',
    value: '18 days',
    delta: '-2 days',
    trend: [24, 23, 22, 21, 20, 19, 18]
  },
  {
    id: 'PM-3',
    title: 'Change request approval rate',
    value: '71%',
    delta: '+3% MoM',
    trend: [60, 63, 61, 65, 67, 70, 71]
  },
  {
    id: 'PM-4',
    title: 'Requirements with AI analysis',
    value: '54%',
    delta: '+9% QoQ',
    trend: [32, 36, 38, 41, 47, 50, 54]
  }
];

export const projectInfo = {
  platform: 'Requirements Control Tower',
  project: 'Unified Product Enablement',
  manager: 'Taylor Brooks'
};

export const teamMembers = [
  { id: 'USR-1', name: 'Alex Johnson', initials: 'AJ', role: 'Product Owner' },
  { id: 'USR-2', name: 'Priya Patel', initials: 'PP', role: 'Compliance Lead' },
  { id: 'USR-3', name: 'Chen Wei', initials: 'CW', role: 'AI Architect' }
];
