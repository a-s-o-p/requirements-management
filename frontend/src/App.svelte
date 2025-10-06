<script>
  import { onMount } from 'svelte';
  import Dashboard from './components/Dashboard.svelte';
  import ExpectationsTable from './components/ExpectationsTable.svelte';
  import RequirementsTable from './components/RequirementsTable.svelte';
  import ChangeRequestTable from './components/ChangeRequestTable.svelte';
  import Modal from './components/Modal.svelte';
  import FormField from './components/FormField.svelte';
  import SearchGroup from './components/SearchGroup.svelte';
  import {
    expectations as expectationSeed,
    requirements as requirementSeed,
    changeRequests as changeRequestSeed,
    activityLog as activitySeed,
    bottlenecks as bottleneckSeed,
    projectMetrics as metricSeed,
    metricDefinitions,
    projectInfo,
    teamMembers
  } from './lib/data';

  const primaryNav = [
    { id: 'dashboard', label: 'Dashboard', icon: 'grid' },
    { id: 'expectations', label: 'Expectations', icon: 'sparkles' },
    { id: 'requirements', label: 'Requirements', icon: 'document-text' },
    { id: 'changeRequests', label: 'Change Requests', icon: 'arrows-right-left' }
  ];

  const dashboardNav = primaryNav[0];
  const lifecycleNav = primaryNav.slice(1);

  let activeView = 'dashboard';
  let sidebarCollapsed = false;
  let isMobileMenuOpen = false;

  let expectations = expectationSeed.map((record) => ({ ...record }));
  let requirements = requirementSeed.map((record) => ({ ...record }));
  let changeRequests = changeRequestSeed.map((record) => ({ ...record }));
  let activityLog = activitySeed.map((entry) => ({ ...entry }));
  let bottlenecks = bottleneckSeed.map((entry) => ({ ...entry }));
  let projectMetrics = metricSeed.map((metric) => ({ ...metric }));

  let searchQuery = '';
  let searchFocused = false;
  let showSearchDropdown = false;
  let notifyModalOpen = false;
  let notifyComment = '';

  let quickActionOpen = false;
  let userMenuOpen = false;

  let expectationFilters = {
    search: '',
    status: new Set(),
    priority: 'All',
    domain: 'All',
    iceMin: 0,
    iceMax: 30
  };

  let requirementFilters = {
    search: '',
    status: 'All',
    priority: 'All',
    assignee: 'All',
    progressMin: 0,
    progressMax: 100,
    source: 'All'
  };

  let changeRequestFilters = {
    search: '',
    status: 'All',
    priority: 'All',
    linkedRequirement: 'All',
    impact: 'All',
    analysisStatus: 'All'
  };

  let expectationSort = { field: 'title', direction: 'asc' };
  let requirementSort = { field: 'title', direction: 'asc' };
  let changeRequestSort = { field: 'title', direction: 'asc' };

  let detailView = null;
  let detailTab = 'overview';

  let linkPanelOpen = false;
  let linkTargetExpectation = null;

  let createModals = {
    expectation: false,
    requirement: false,
    changeRequest: false
  };

  let newExpectation = {
    title: '',
    owner: '',
    priority: 'Medium',
    domain: '',
    summary: ''
  };

  let newRequirement = {
    title: '',
    assignee: '',
    priority: 'Medium',
    source: '',
    summary: ''
  };

  let newChangeRequest = {
    title: '',
    owner: '',
    priority: 'Medium',
    linkedRequirement: '',
    impact: 'Medium',
    analysisStatus: 'Not started',
    summary: ''
  };

  let metricHistoryModal = { open: false, metric: null, window: 7 };

  const statusColors = {
    Approved: 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/40',
    'Awaiting Review': 'bg-amber-500/15 text-amber-300 border border-amber-500/40',
    'Clarification Needed': 'bg-rose-500/15 text-rose-300 border border-rose-500/40',
    Draft: 'bg-slate-500/15 text-slate-300 border border-slate-500/40',
    'Impact Analysis': 'bg-sky-500/15 text-sky-300 border border-sky-500/40',
    Implemented: 'bg-emerald-500/15 text-emerald-200 border border-emerald-500/40',
    'DoR Ready': 'bg-indigo-500/15 text-indigo-200 border border-indigo-500/40'
  };

  const priorityColors = {
    High: 'bg-rose-500/20 text-rose-200',
    Medium: 'bg-amber-500/20 text-amber-200',
    Low: 'bg-sky-500/20 text-sky-200'
  };

  const severityColors = {
    Warning: 'bg-amber-500/10 text-amber-300 border border-amber-500/40',
    Critical: 'bg-rose-600/10 text-rose-200 border border-rose-500/40'
  };

  const impactColors = {
    High: 'bg-rose-500/20 text-rose-100',
    Medium: 'bg-amber-500/20 text-amber-100',
    Low: 'bg-sky-500/20 text-sky-100'
  };

  let activityFilter = 'All';

  onMount(() => {
    const resizeHandler = () => {
      sidebarCollapsed = window.innerWidth < 1280;
    };
    resizeHandler();
    window.addEventListener('resize', resizeHandler);
    return () => window.removeEventListener('resize', resizeHandler);
  });

  $: searchTerm = searchQuery.trim().toLowerCase();
  $: groupedSearchResults = searchTerm
    ? {
        expectations: expectations.filter((exp) => matchesSearch(exp)),
        requirements: requirements.filter((req) => matchesSearch(req)),
        changeRequests: changeRequests.filter((cr) => matchesSearch(cr))
      }
    : { expectations: [], requirements: [], changeRequests: [] };

  $: totalSearchResults =
    groupedSearchResults.expectations.length +
    groupedSearchResults.requirements.length +
    groupedSearchResults.changeRequests.length;

  $: filteredExpectations = expectations
    .filter(applyExpectationFilters)
    .sort((a, b) => tableSort(a, b, expectationSort.field, expectationSort.direction));

  $: filteredRequirements = requirements
    .filter(applyRequirementFilters)
    .sort((a, b) => tableSort(a, b, requirementSort.field, requirementSort.direction));

  $: filteredChangeRequests = changeRequests
    .filter(applyChangeRequestFilters)
    .sort((a, b) => tableSort(a, b, changeRequestSort.field, changeRequestSort.direction));

  $: summaryCounts = {
    expectations: expectations.length,
    requirements: requirements.length,
    changeRequests: changeRequests.length
  };

  function matchesSearch(record) {
    const values = Object.values(record).flatMap((value) => {
      if (Array.isArray(value)) return value;
      if (typeof value === 'object' && value !== null) return Object.values(value);
      return value;
    });
    return values
      .join(' ')
      .toLowerCase()
      .includes(searchTerm);
  }

  function highlightMatch(text) {
    if (!searchTerm) return text;
    const safeTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${safeTerm})`, 'gi');
    return text.replace(regex, '<mark class="bg-amber-400/40 text-amber-100 rounded px-0.5">$1</mark>');
  }

  function applyExpectationFilters(record) {
    const { search, status, priority, domain, iceMin, iceMax } = expectationFilters;
    const matchesSearchValue = !search || record.title.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = status.size === 0 || status.has(record.status);
    const matchesPriority = priority === 'All' || record.priority === priority;
    const matchesDomain = domain === 'All' || record.domain === domain;
    const matchesIce = record.iceScore >= iceMin && record.iceScore <= iceMax;
    return matchesSearchValue && matchesStatus && matchesPriority && matchesDomain && matchesIce;
  }

  function applyRequirementFilters(record) {
    const { search, status, priority, assignee, progressMin, progressMax, source } = requirementFilters;
    const matchesSearchValue = !search || record.title.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = status === 'All' || record.status === status;
    const matchesPriority = priority === 'All' || record.priority === priority;
    const matchesAssignee = assignee === 'All' || record.assignee === assignee;
    const matchesProgress = record.progress >= progressMin && record.progress <= progressMax;
    const matchesSource = source === 'All' || record.source === source;
    return matchesSearchValue && matchesStatus && matchesPriority && matchesAssignee && matchesProgress && matchesSource;
  }

  function applyChangeRequestFilters(record) {
    const { search, status, priority, linkedRequirement, impact, analysisStatus } = changeRequestFilters;
    const matchesSearchValue = !search || record.title.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = status === 'All' || record.status === status;
    const matchesPriority = priority === 'All' || record.priority === priority;
    const matchesImpact = impact === 'All' || record.impact === impact;
    const matchesAnalysis = analysisStatus === 'All' || record.analysisStatus === analysisStatus;
    const matchesLinked =
      linkedRequirement === 'All' || record.linkedRequirements?.some((reqId) => reqId === linkedRequirement);
    return matchesSearchValue && matchesStatus && matchesPriority && matchesImpact && matchesAnalysis && matchesLinked;
  }

  function tableSort(a, b, field, direction) {
    const valueA = getComparableValue(a, field);
    const valueB = getComparableValue(b, field);
    if (valueA < valueB) return direction === 'asc' ? -1 : 1;
    if (valueA > valueB) return direction === 'asc' ? 1 : -1;
    return 0;
  }

  function getComparableValue(record, field) {
    if (Array.isArray(record[field])) {
      return record[field].length;
    }
    const value = record[field];
    if (typeof value === 'string') return value.toLowerCase();
    return value ?? '';
  }

  function toggleSort(currentSort, field) {
    if (currentSort.field === field) {
      return { field, direction: currentSort.direction === 'asc' ? 'desc' : 'asc' };
    }
    return { field, direction: 'asc' };
  }

  function openDetail(type, item) {
    detailView = { type, item };
    detailTab = 'overview';
  }

  function closeDetail() {
    detailView = null;
  }

  function openLinkPanel(expectation) {
    linkTargetExpectation = expectation;
    linkPanelOpen = true;
  }

  function closeLinkPanel() {
    linkPanelOpen = false;
    linkTargetExpectation = null;
  }

  function linkExpectationToRequirement(expectationId, requirementId) {
    expectations = expectations.map((exp) =>
      exp.id === expectationId && !exp.linkedRequirements.includes(requirementId)
        ? { ...exp, linkedRequirements: [...exp.linkedRequirements, requirementId] }
        : exp
    );
    requirements = requirements.map((req) =>
      req.id === requirementId && !req.relatedExpectations.includes(expectationId)
        ? { ...req, relatedExpectations: [...req.relatedExpectations, expectationId] }
        : req
    );
    activityLog = [
      {
        id: `ACT-${activityLog.length + 1}`,
        type: 'Link',
        action: `Linked ${expectationId} → ${requirementId}`,
        timestamp: 'Just now',
        author: 'You'
      },
      ...activityLog
    ];
    closeLinkPanel();
  }

  function createRequirementFromExpectation(expectation) {
    createModals.requirement = true;
    newRequirement = {
      title: `${expectation.title} Requirement`,
      assignee: expectation.owner,
      priority: 'Medium',
      source: expectation.id,
      summary: expectation.summary
    };
  }

  function openCreateModal(type) {
    createModals = { ...createModals, [type]: true };
    if (type === 'changeRequest' && requirements.length) {
      newChangeRequest.linkedRequirement = requirements[0].id;
    }
  }

  function closeCreateModal(type) {
    createModals = { ...createModals, [type]: false };
  }

  function addExpectation() {
    if (!newExpectation.title.trim()) return;
    const id = `EXP-${String(expectations.length + 1).padStart(3, '0')}`;
    const record = {
      id,
      title: newExpectation.title,
      owner: newExpectation.owner || 'Unassigned',
      status: 'Draft',
      priority: newExpectation.priority,
      domain: newExpectation.domain || 'General',
      version: '0.1.0',
      impact: 0,
      ice: { impact: 0, confidence: 0, ease: 0 },
      iceScore: 0,
      flags: [],
      mosCow: 'Should',
      metrics: [],
      conflicts: [],
      tags: [],
      linkedRequirements: [],
      summary: newExpectation.summary
    };
    expectations = [record, ...expectations];
    activityLog = [
      { id: `ACT-${activityLog.length + 1}`, type: 'Expectation', action: `Added ${id}`, timestamp: 'Just now', author: 'You' },
      ...activityLog
    ];
    newExpectation = { title: '', owner: '', priority: 'Medium', domain: '', summary: '' };
    closeCreateModal('expectation');
  }

  function addRequirement() {
    if (!newRequirement.title.trim()) return;
    const id = `REQ-${String(requirements.length + 101).padStart(3, '0')}`;
    const record = {
      id,
      title: newRequirement.title,
      status: 'Draft',
      lastUpdated: new Date().toISOString().slice(0, 10),
      version: '0.1.0',
      priority: newRequirement.priority,
      assignee: newRequirement.assignee || 'Unassigned',
      progress: 0,
      source: newRequirement.source || 'Manual',
      relatedExpectations: newRequirement.source ? [newRequirement.source] : [],
      linkedChangeRequests: [],
      owner: newRequirement.assignee || 'Unassigned',
      readiness: [],
      metrics: []
    };
    requirements = [record, ...requirements];
    if (newRequirement.source) {
      expectations = expectations.map((exp) =>
        exp.id === newRequirement.source
          ? { ...exp, linkedRequirements: Array.from(new Set([...(exp.linkedRequirements || []), id])) }
          : exp
      );
    }
    activityLog = [
      { id: `ACT-${activityLog.length + 1}`, type: 'Requirement', action: `Added ${id}`, timestamp: 'Just now', author: 'You' },
      ...activityLog
    ];
    newRequirement = { title: '', assignee: '', priority: 'Medium', source: '', summary: '' };
    closeCreateModal('requirement');
  }

  function addChangeRequest() {
    if (!newChangeRequest.title.trim()) return;
    const id = `CR-${String(changeRequests.length + 12).padStart(2, '0')}`;
    const record = {
      id,
      title: newChangeRequest.title,
      status: 'Draft',
      submitted: new Date().toISOString().slice(0, 10),
      owner: newChangeRequest.owner || 'Unassigned',
      priority: newChangeRequest.priority,
      linkedRequirements: newChangeRequest.linkedRequirement ? [newChangeRequest.linkedRequirement] : [],
      impact: newChangeRequest.impact,
      analysisStatus: newChangeRequest.analysisStatus,
      version: 'Proposed 0.1.0',
      decisions: [],
      impactSummary: newChangeRequest.summary
    };
    changeRequests = [record, ...changeRequests];
    if (newChangeRequest.linkedRequirement) {
      requirements = requirements.map((req) =>
        req.id === newChangeRequest.linkedRequirement
          ? {
              ...req,
              linkedChangeRequests: Array.from(new Set([...(req.linkedChangeRequests || []), record.id]))
            }
          : req
      );
    }
    activityLog = [
      { id: `ACT-${activityLog.length + 1}`, type: 'Change Request', action: `Added ${id}`, timestamp: 'Just now', author: 'You' },
      ...activityLog
    ];
    newChangeRequest = {
      title: '',
      owner: '',
      priority: 'Medium',
      linkedRequirement: '',
      impact: 'Medium',
      analysisStatus: 'Not started',
      summary: ''
    };
    closeCreateModal('changeRequest');
  }

  function openChangeRequestWizard(requirement) {
    createModals.changeRequest = true;
    newChangeRequest = {
      title: `Change for ${requirement.title}`,
      owner: requirement.assignee,
      priority: requirement.priority,
      linkedRequirement: requirement.id,
      impact: 'Medium',
      analysisStatus: 'Not started',
      summary: ''
    };
  }

  function implementChangeRequest(changeRequest) {
    changeRequests = changeRequests.map((cr) =>
      cr.id === changeRequest.id ? { ...cr, status: 'Implemented', analysisStatus: 'Complete' } : cr
    );
    changeRequest.linkedRequirements?.forEach((reqId) => {
      requirements = requirements.map((req) =>
        req.id === reqId
          ? {
              ...req,
              version: incrementVersion(req.version),
              status: 'Approved',
              progress: Math.min(100, req.progress + 10)
            }
          : req
      );
    });
    activityLog = [
      {
        id: `ACT-${activityLog.length + 1}`,
        type: 'Implementation',
        action: `Implemented ${changeRequest.id}`,
        timestamp: 'Just now',
        author: 'You'
      },
      ...activityLog
    ];
    closeDetail();
  }

  function incrementVersion(version) {
    if (!version) return '1.0.0';
    const parts = version.split('.').map((part) => parseInt(part, 10));
    if (parts.length !== 3 || parts.some((n) => Number.isNaN(n))) return version;
    parts[2] += 1;
    return `${parts[0]}.${parts[1]}.${parts[2]}`;
  }

  function navigateTo(target) {
    activeView = target;
  }

  function openMetricHistory(metric) {
    metricHistoryModal = { open: true, metric, window: 7 };
  }

  function closeMetricHistory() {
    metricHistoryModal = { open: false, metric: null, window: 7 };
  }

  function handleSearchNavigation(type, record) {
    activeView = type;
    const detailType = type === 'changeRequests' ? 'changeRequest' : type.slice(0, -1);
    openDetail(detailType, record);
    resetSearch();
  }

  function resetSearch() {
    searchQuery = '';
    showSearchDropdown = false;
  }

  function sidebarIcon(name) {
    if (name === 'grid') {
      return '<svg class="h-4 w-4 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25A2.25 2.25 0 0 1 8.25 10.5H6A2.25 2.25 0 0 1 3.75 8.25V6Zm9.75 0A2.25 2.25 0 0 1 15.75 3.75H18a2.25 2.25 0 0 1 2.25 2.25v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25Zm9.75 0A2.25 2.25 0 0 1 15.75 13.5H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"/></svg>';
    }
    if (name === 'sparkles') {
      return '<svg class="h-4 w-4 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.847-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.847a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.847.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3 3 0 0 0-2.206-2.206L14.5 6.25l1.035-.259a3 3 0 0 0 2.206-2.206L18 2.75l.259 1.035a3 3 0 0 0 2.206 2.206L21.5 6.25l-1.035.259a3 3 0 0 0-2.206 2.206ZM16.894 20.567 16.5 22.001l-.394-1.434a3.75 3.75 0 0 0-2.673-2.673L12 17.5l1.433-.394a3.75 3.75 0 0 0 2.673-2.673L16.5 13l.394 1.433a3.75 3.75 0 0 0 2.673 2.673L21 17.5l-1.433.394a3.75 3.75 0 0 0-2.673 2.673Z"/></svg>';
    }
    if (name === 'document-text') {
      return '<svg class="h-4 w-4 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75h6m-6 3.75h6m-6 3.75h6M6.75 7.5h.75m-.75 3.75h.75m-.75 3.75h.75M5.25 4.125c0-.621.504-1.125 1.125-1.125h13.5c.621 0 1.125.504 1.125 1.125v15.75c0 .621-.504 1.125-1.125 1.125h-13.5A1.125 1.125 0 0 1 5.25 19.875V4.125Z"/></svg>';
    }
    return '<svg class="h-4 w-4 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992m0 0v4.992m0-4.992-6.928 6.928a4.5 4.5 0 0 1-6.364 0l-2.122-2.12a4.5 4.5 0 0 1 0-6.364l6.364-6.365"/></svg>';
  }

  function statusBadge(status) {
    return statusColors[status] || 'bg-slate-600/20 text-slate-200 border border-slate-500/50';
  }

  function priorityBadge(priority) {
    return priorityColors[priority] || 'bg-slate-500/20 text-slate-100';
  }

  function severityBadge(severity) {
    return severityColors[severity] || 'bg-slate-500/15 text-slate-200 border border-slate-500/40';
  }

  function openNotify() {
    notifyModalOpen = true;
    notifyComment = searchQuery;
  }

  function submitNotify() {
    activityLog = [
      {
        id: `ACT-${activityLog.length + 1}`,
        type: 'Alert',
        action: `Escalated search: ${notifyComment || 'No query'}`,
        timestamp: 'Just now',
        author: 'You'
      },
      ...activityLog
    ];
    notifyComment = '';
    notifyModalOpen = false;
    resetSearch();
  }
</script>

<svelte:window
  on:click={(event) => {
    const path = event.composedPath?.() || [];
    if (!path.some((node) => node?.dataset?.menu === 'quick-actions')) {
      quickActionOpen = false;
    }
    if (!path.some((node) => node?.dataset?.menu === 'user-menu')) {
      userMenuOpen = false;
    }
  }}
/>

<div class="flex h-screen bg-slate-950 text-slate-100">
  <aside
    class={`${sidebarCollapsed && !isMobileMenuOpen ? 'hidden xl:flex' : 'flex'} w-[300px] shrink-0 flex-col border-r border-slate-800 bg-slate-950/95 backdrop-blur-xl`}
  >
    <div class="flex items-center gap-3 px-6 pt-6 pb-4">
      <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-sky-500 font-semibold text-slate-900">
        RC
      </div>
      <div class="flex flex-col overflow-hidden">
        <span class="text-sm font-semibold text-slate-100">{projectInfo.platform}</span>
        <span class="truncate text-xs text-slate-400" title={projectInfo.project}>{projectInfo.project}</span>
      </div>
    </div>
    <nav class="mt-2 flex-1 overflow-y-auto px-3">
      <div class="space-y-1">
        <button
          class={`group flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm transition ${
            activeView === dashboardNav.id
              ? 'bg-indigo-500/20 text-indigo-200 ring-1 ring-inset ring-indigo-400/50'
              : 'text-slate-300 hover:bg-slate-800/60 hover:text-white focus-visible:ring-1 focus-visible:ring-indigo-400/50'
          }`}
          on:click={() => {
            activeView = dashboardNav.id;
            isMobileMenuOpen = false;
          }}
        >
          <span class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800 bg-slate-900/80">
            {@html sidebarIcon(dashboardNav.icon)}
          </span>
          <span class="text-left">{dashboardNav.label}</span>
        </button>
      </div>
      <div class="mt-6">
        <div class="flex items-center justify-between px-1">
          <h3 class="text-sm font-semibold text-slate-100">Lifecycle Flow</h3>
          <span class="rounded-full bg-indigo-500/20 px-2 py-0.5 text-[11px] uppercase tracking-wide text-indigo-200">Guided</span>
        </div>
        <div class="mt-3 rounded-2xl border border-slate-800 bg-slate-900/60 p-4 shadow-inner">
          <p class="text-xs leading-relaxed text-slate-400">
            Expectations move forward into Requirements, which evolve through Change Requests and return as updated Requirements.
          </p>
          <div class="mt-4 flex flex-col gap-3 text-sm">
            {#each lifecycleNav as item, index}
              <div class="relative">
                <button
                  class={`group flex w-full items-center justify-between rounded-2xl border px-3 py-2 text-left transition ${
                    activeView === item.id
                      ? 'border-indigo-400/60 bg-indigo-500/15 text-indigo-100 shadow-[0_0_0_1px] shadow-indigo-400/40'
                      : 'border-slate-800 bg-slate-900/70 text-slate-200 hover:border-indigo-500/50 hover:bg-indigo-500/10 focus-visible:ring-1 focus-visible:ring-indigo-400/50'
                  }`}
                  on:click={() => {
                    navigateTo(item.id);
                    isMobileMenuOpen = false;
                  }}
                >
                  <div class="flex items-center gap-3">
                    <span class={`flex h-9 w-9 items-center justify-center rounded-xl border ${
                      activeView === item.id
                        ? 'border-indigo-400/80 bg-indigo-500/20 text-indigo-100'
                        : 'border-slate-800 bg-slate-900/80 text-slate-300'
                    }`}>
                      {@html sidebarIcon(item.icon)}
                    </span>
                    <span class="font-medium">{item.label}</span>
                  </div>
                  <span class="text-xs text-slate-500">{summaryCounts[item.id] ?? 0}</span>
                </button>
                {#if index < lifecycleNav.length - 1}
                  <div class="pointer-events-none mt-2 flex items-center justify-center">
                    <div class="flex items-center gap-2 text-slate-500">
                      <div class="h-10 w-0.5 bg-gradient-to-b from-indigo-500/50 via-emerald-500/50 to-amber-500/50"></div>
                      <svg class="h-4 w-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8 5h8m0 0-3-3m3 3-3 3M16 19H8m0 0 3 3m-3-3 3-3" />
                      </svg>
                      <div class="h-10 w-0.5 bg-gradient-to-b from-amber-500/50 via-sky-500/50 to-rose-500/50"></div>
                    </div>
                  </div>
                {/if}
              </div>
            {/each}
            <div class="flex flex-col items-center gap-2 pt-1 text-xs text-indigo-200">
              <svg class="h-8 w-8 text-indigo-300" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M26 10v10a6 6 0 0 1-6 6H9.5" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.5 26 13 22.5M9.5 26l3.5 3.5" />
              </svg>
              <button
                class="rounded-full border border-indigo-500/60 bg-indigo-500/15 px-3 py-1 text-[11px] font-medium uppercase tracking-wide text-indigo-100 hover:border-indigo-400/70 hover:bg-indigo-500/25"
                on:click={() => navigateTo('requirements')}
              >
                Updated Requirements
              </button>
              <span class="text-[11px] text-indigo-200/70">Continuous improvement loop</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
    <div class="px-6 pb-6 pt-4 text-xs text-slate-500">
      Managed by {projectInfo.manager}
    </div>
  </aside>

  <div class="flex min-w-0 flex-1 flex-col">
    <header class="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div class="flex items-center gap-4 px-4 py-3 md:px-6">
        <button class="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-800 bg-slate-900/70 text-slate-300 hover:bg-slate-800 xl:hidden" on:click={() => (isMobileMenuOpen = !isMobileMenuOpen)} aria-label="Toggle menu">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <div class="relative mx-auto hidden flex-1 md:block">
          <svg class="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1 0 6.75 6.75a7.5 7.5 0 0 0 9.9 9.9Z" />
          </svg>
          <input
            class="w-full rounded-2xl border border-slate-800 bg-slate-900/70 py-3 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/30"
            type="search"
            placeholder="Search across Expectations, Requirements, Change Requests in natural language…"
            value={searchQuery}
            on:input={(event) => {
              searchQuery = event.target.value;
              showSearchDropdown = !!event.target.value.trim();
            }}
            on:focus={() => {
              searchFocused = true;
              showSearchDropdown = !!searchQuery.trim();
            }}
            on:blur={() => {
              searchFocused = false;
              setTimeout(() => (showSearchDropdown = false), 120);
            }}
          />
          {#if showSearchDropdown && searchQuery.trim()}
            <div class="absolute left-0 right-0 z-20 mt-2 max-h-96 overflow-y-auto rounded-2xl border border-slate-800/60 bg-slate-900/95 p-3 shadow-2xl">
              {#if totalSearchResults === 0}
                <div class="flex flex-col items-center gap-3 rounded-xl border border-dashed border-slate-700 bg-slate-900/60 p-6 text-center text-sm text-slate-300">
                  <span>Ничего не найдено</span>
                  <button class="rounded-full bg-indigo-500/20 px-4 py-1 text-xs font-medium text-indigo-200 hover:bg-indigo-500/30" on:click={openNotify}>
                    Notify Project Manager
                  </button>
                </div>
              {:else}
                {#if groupedSearchResults.expectations.length}
                  <SearchGroup
                    label="Expectations"
                    items={groupedSearchResults.expectations}
                    count={groupedSearchResults.expectations.length}
                    {highlightMatch}
                    on:view={(event) => handleSearchNavigation('expectations', event.detail)}
                    on:viewAll={() => navigateTo('expectations')}
                  />
                {/if}
                {#if groupedSearchResults.requirements.length}
                  <SearchGroup
                    label="Requirements"
                    items={groupedSearchResults.requirements}
                    count={groupedSearchResults.requirements.length}
                    {highlightMatch}
                    on:view={(event) => handleSearchNavigation('requirements', event.detail)}
                    on:viewAll={() => navigateTo('requirements')}
                  />
                {/if}
                {#if groupedSearchResults.changeRequests.length}
                  <SearchGroup
                    label="Change Requests"
                    items={groupedSearchResults.changeRequests}
                    count={groupedSearchResults.changeRequests.length}
                    {highlightMatch}
                    on:view={(event) => handleSearchNavigation('changeRequests', event.detail)}
                    on:viewAll={() => navigateTo('changeRequests')}
                  />
                {/if}
              {/if}
            </div>
          {/if}
        </div>
        <div class="ml-auto flex items-center gap-2">
          <div class="relative" data-menu="quick-actions">
            <button class="flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900/70 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800" on:click={() => (quickActionOpen = !quickActionOpen)}>
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              <span>Quick Actions</span>
            </button>
            {#if quickActionOpen}
              <div class="absolute right-0 mt-2 w-56 rounded-2xl border border-slate-800 bg-slate-900/95 p-2 shadow-xl">
                <button class="flex w-full items-center justify-between rounded-xl px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-800" on:click={() => { openCreateModal('expectation'); quickActionOpen = false; }}>
                  <span>Add Expectation</span>
                  <svg class="h-4 w-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-3-3v6m9 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                  </svg>
                </button>
                <button class="flex w-full items-center justify-between rounded-xl px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-800" on:click={() => { openCreateModal('requirement'); quickActionOpen = false; }}>
                  <span>Add Requirement</span>
                  <svg class="h-4 w-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-3-3v6m9 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                  </svg>
                </button>
                <button class="flex w-full items-center justify-between rounded-xl px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-800" on:click={() => { openCreateModal('changeRequest'); quickActionOpen = false; }}>
                  <span>Add Change Request</span>
                  <svg class="h-4 w-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-3-3v6m9 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
                  </svg>
                </button>
              </div>
            {/if}
          </div>
          <div class="relative" data-menu="user-menu">
            <button class="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-900/70 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800" on:click={() => (userMenuOpen = !userMenuOpen)}>
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500/70 font-semibold text-slate-900">{teamMembers[0].initials}</div>
              <div class="hidden text-left md:block">
                <div class="text-xs text-slate-400">{teamMembers[0].role}</div>
                <div class="text-sm font-medium text-slate-100">{teamMembers[0].name}</div>
              </div>
            </button>
            {#if userMenuOpen}
              <div class="absolute right-0 mt-2 w-48 rounded-2xl border border-slate-800 bg-slate-900/95 p-2 text-sm text-slate-200 shadow-xl">
                <button class="w-full rounded-xl px-3 py-2 text-left hover:bg-slate-800">Profile</button>
                <button class="w-full rounded-xl px-3 py-2 text-left hover:bg-slate-800">Settings</button>
                <button class="w-full rounded-xl px-3 py-2 text-left text-rose-200 hover:bg-rose-500/10">Sign out</button>
              </div>
            {/if}
          </div>
        </div>
      </div>
      <div class="block border-t border-slate-800 px-4 py-3 md:hidden">
        <div class="relative">
          <input
            class="w-full rounded-xl border border-slate-800 bg-slate-900/80 py-2 pl-10 pr-3 text-sm text-slate-100 placeholder-slate-500"
            type="search"
            placeholder="Tap to search..."
            value={searchQuery}
            on:input={(event) => {
              searchQuery = event.target.value;
              showSearchDropdown = !!event.target.value.trim();
            }}
          />
          <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1 0 6.75 6.75a7.5 7.5 0 0 0 9.9 9.9Z" />
          </svg>
        </div>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto">
      {#if activeView === 'dashboard'}
        <Dashboard
          {projectMetrics}
          {activityLog}
          {bottlenecks}
          {summaryCounts}
          bind:activityFilter
          on:openMetric={(event) => openMetricHistory(event.detail)}
          on:navigate={(event) => navigateTo(event.detail)}
          {severityBadge}
        />
      {:else if activeView === 'expectations'}
        <ExpectationsTable
          items={filteredExpectations}
          allItems={expectations}
          filters={expectationFilters}
          sort={expectationSort}
          on:updateFilters={(event) => (expectationFilters = event.detail)}
          on:updateSort={(event) => (expectationSort = toggleSort(expectationSort, event.detail))}
          on:view={(event) => openDetail('expectation', event.detail)}
          on:link={(event) => openLinkPanel(event.detail)}
          on:create={() => openCreateModal('expectation')}
          {statusBadge}
          {priorityBadge}
        />
      {:else if activeView === 'requirements'}
        <RequirementsTable
          items={filteredRequirements}
          allItems={requirements}
          filters={requirementFilters}
          sort={requirementSort}
          on:updateFilters={(event) => (requirementFilters = event.detail)}
          on:updateSort={(event) => (requirementSort = toggleSort(requirementSort, event.detail))}
          on:view={(event) => openDetail('requirement', event.detail)}
          on:changeRequest={(event) => openChangeRequestWizard(event.detail)}
          on:create={() => openCreateModal('requirement')}
          {statusBadge}
          {priorityBadge}
        />
      {:else if activeView === 'changeRequests'}
        <ChangeRequestTable
          items={filteredChangeRequests}
          allItems={changeRequests}
          filters={changeRequestFilters}
          sort={changeRequestSort}
          on:updateFilters={(event) => (changeRequestFilters = event.detail)}
          on:updateSort={(event) => (changeRequestSort = toggleSort(changeRequestSort, event.detail))}
          on:view={(event) => openDetail('changeRequest', event.detail)}
          on:implement={(event) => implementChangeRequest(event.detail)}
          on:create={() => openCreateModal('changeRequest')}
          {statusBadge}
          {priorityBadge}
          {impactColors}
        />
      {/if}
    </main>
  </div>
</div>

{#if linkPanelOpen && linkTargetExpectation}
  <div class="fixed inset-0 z-40 flex justify-end bg-slate-950/40 backdrop-blur-sm" role="dialog" aria-modal="true">
    <div class="h-full w-full max-w-md border-l border-slate-800 bg-slate-900/95 p-6 shadow-2xl">
      <div class="flex items-start justify-between">
        <div>
          <h3 class="text-lg font-semibold text-slate-100">Link to Requirements</h3>
          <p class="mt-1 text-sm text-slate-400">Connect {linkTargetExpectation.id} to an existing requirement or create a new one.</p>
        </div>
        <button class="rounded-full border border-slate-700 p-1 text-slate-400 hover:text-white" on:click={closeLinkPanel} aria-label="Close link panel">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="m6 18 12-12M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="mt-6 space-y-4">
        <div class="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <div class="text-sm font-medium text-slate-200">{linkTargetExpectation.title}</div>
          <div class="mt-2 text-xs text-slate-400">Domain • {linkTargetExpectation.domain} · Priority • {linkTargetExpectation.priority}</div>
        </div>
        <div class="space-y-3">
          {#each requirements as requirement}
            <button class="flex w-full items-center justify-between rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-left text-sm text-slate-200 hover:border-indigo-500/50 hover:bg-indigo-500/10" on:click={() => linkExpectationToRequirement(linkTargetExpectation.id, requirement.id)}>
              <div>
                <div class="font-medium">{requirement.id} · {requirement.title}</div>
                <div class="text-xs text-slate-400">{requirement.status} · {requirement.assignee}</div>
              </div>
              <svg class="h-4 w-4 text-indigo-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          {/each}
        </div>
        <div class="rounded-2xl border border-dashed border-indigo-500/50 bg-indigo-500/10 p-4 text-center">
          <p class="text-sm text-indigo-100">Need a new requirement?</p>
          <button class="mt-3 inline-flex items-center gap-2 rounded-full bg-indigo-500 px-4 py-2 text-xs font-semibold text-slate-950 shadow hover:bg-indigo-400" on:click={() => createRequirementFromExpectation(linkTargetExpectation)}>
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m6-6H6" />
            </svg>
            Create new Requirement
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

{#if detailView}
  <div class="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/60 backdrop-blur" role="dialog" aria-modal="true">
    <div class="relative w-full max-w-4xl rounded-3xl border border-slate-800 bg-slate-950/95 p-6 shadow-2xl">
      <button class="absolute right-6 top-6 rounded-full border border-slate-700 p-1 text-slate-400 hover:text-white" on:click={closeDetail} aria-label="Close detail view">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="m6 18 12-12M6 6l12 12" />
        </svg>
      </button>
      <header class="flex flex-wrap items-center gap-4 pr-10">
        <div>
          <h2 class="text-2xl font-semibold text-slate-100">{detailView.item.title}</h2>
          <div class="mt-2 flex flex-wrap gap-2 text-xs text-slate-400">
            <span class={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs ${statusBadge(detailView.item.status)}`}>{detailView.item.status}</span>
            {#if detailView.item.priority}
              <span class={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs ${priorityBadge(detailView.item.priority)}`}>Priority · {detailView.item.priority}</span>
            {/if}
          </div>
        </div>
        <div class="ml-auto flex flex-wrap items-center gap-2">
          <button class="inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-1.5 text-xs text-slate-200 hover:border-indigo-500/50 hover:text-white">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m6-6H6" />
            </svg>
            New conversation
          </button>
          {#if detailView.type === 'changeRequest'}
            <button class="inline-flex items-center gap-2 rounded-full bg-emerald-400 px-4 py-2 text-xs font-semibold text-slate-950 hover:bg-emerald-300" on:click={() => implementChangeRequest(detailView.item)}>
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
              Implement
            </button>
          {/if}
        </div>
      </header>
      <div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[2fr,1fr]">
        <div>
          <nav class="flex gap-3 text-sm">
            {#each ['overview', 'history', 'links', 'analysis', 'discussion'] as tab}
              <button class={`rounded-full px-4 py-1.5 capitalize transition ${detailTab === tab ? 'bg-indigo-500 text-slate-950 font-medium' : 'border border-transparent text-slate-400 hover:border-slate-700 hover:text-slate-200'}`} on:click={() => (detailTab = tab)}>
                {tab}
              </button>
            {/each}
          </nav>
          <div class="mt-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-200">
            {#if detailTab === 'overview'}
              <p class="leading-relaxed text-slate-300">{detailView.item.summary || 'Structured overview coming soon. Populate key fields, business impact, and context to collaborate faster.'}</p>
              <dl class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                {#if detailView.item.owner}
                  <div>
                    <dt class="text-xs uppercase tracking-wide text-slate-400">Owner</dt>
                    <dd class="text-sm text-slate-100">{detailView.item.owner}</dd>
                  </div>
                {/if}
                {#if detailView.item.assignee}
                  <div>
                    <dt class="text-xs uppercase tracking-wide text-slate-400">Assignee</dt>
                    <dd class="text-sm text-slate-100">{detailView.item.assignee}</dd>
                  </div>
                {/if}
                {#if detailView.item.version}
                  <div>
                    <dt class="text-xs uppercase tracking-wide text-slate-400">Version</dt>
                    <dd class="text-sm text-slate-100">{detailView.item.version}</dd>
                  </div>
                {/if}
                {#if detailView.item.domain}
                  <div>
                    <dt class="text-xs uppercase tracking-wide text-slate-400">Domain</dt>
                    <dd class="text-sm text-slate-100">{detailView.item.domain}</dd>
                  </div>
                {/if}
              </dl>
            {:else if detailTab === 'history'}
              <ul class="space-y-3">
                {#each activityLog.filter((entry) => entry.action.includes(detailView.item.id)) as entry}
                  <li class="flex items-start gap-3 rounded-xl border border-slate-800/60 bg-slate-900/40 p-3">
                    <span class="mt-1 h-2 w-2 rounded-full bg-indigo-400"></span>
                    <div>
                      <div class="text-sm text-slate-200">{entry.action}</div>
                      <div class="text-xs text-slate-500">{entry.timestamp} • {entry.author}</div>
                    </div>
                  </li>
                {:else}
                  <li class="rounded-xl border border-dashed border-slate-700 p-6 text-center text-sm text-slate-400">History is building as the team collaborates.</li>
                {/each}
              </ul>
            {:else if detailTab === 'links'}
              <div class="space-y-4">
                {#if detailView.item.relatedExpectations?.length}
                  <section>
                    <h4 class="text-xs uppercase tracking-wide text-slate-400">Linked Expectations</h4>
                    <div class="mt-2 space-y-2">
                      {#each detailView.item.relatedExpectations as expId}
                        <div class="rounded-xl border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-200">{expId}</div>
                      {/each}
                    </div>
                  </section>
                {/if}
                {#if detailView.item.linkedRequirements?.length}
                  <section>
                    <h4 class="text-xs uppercase tracking-wide text-slate-400">Linked Requirements</h4>
                    <div class="mt-2 space-y-2">
                      {#each detailView.item.linkedRequirements as reqId}
                        <div class="rounded-xl border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-200">{reqId}</div>
                      {/each}
                    </div>
                  </section>
                {/if}
                {#if detailView.item.linkedChangeRequests?.length}
                  <section>
                    <h4 class="text-xs uppercase tracking-wide text-slate-400">Change Requests</h4>
                    <div class="mt-2 space-y-2">
                      {#each detailView.item.linkedChangeRequests as crId}
                        <div class="rounded-xl border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-200">{crId}</div>
                      {/each}
                    </div>
                  </section>
                {/if}
              </div>
            {:else if detailTab === 'analysis'}
              <div class="space-y-3 text-sm text-slate-300">
                <p>AI assessments, readiness insights, and risk scoring surface here. Attach evidence or trigger deeper evaluations directly.</p>
                <div class="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                  <h4 class="text-xs uppercase tracking-wide text-slate-400">Recommended next step</h4>
                  <p class="mt-2 text-sm text-slate-200">Review outstanding clarifications and confirm acceptance criteria to unblock downstream changes.</p>
                </div>
              </div>
            {:else if detailTab === 'discussion'}
              <div class="space-y-4">
                <div class="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
                  <p class="text-sm text-slate-300">Kick off a discussion to align with stakeholders. Mention teammates with @ and attach insights from AI analyses.</p>
                </div>
                <textarea class="min-h-[120px] w-full rounded-2xl border border-slate-800 bg-slate-950/40 p-3 text-sm text-slate-100 placeholder-slate-500 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/30" placeholder="Share an update…"></textarea>
                <div class="flex justify-end">
                  <button class="rounded-full bg-indigo-500 px-4 py-2 text-xs font-semibold text-slate-950 hover:bg-indigo-400">Post update</button>
                </div>
              </div>
            {/if}
          </div>
        </div>
        <aside class="space-y-4">
          <div class="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <h4 class="text-xs uppercase tracking-wide text-slate-400">Key attributes</h4>
            <dl class="mt-3 space-y-2 text-sm">
              {#if detailView.item.priority}
                <div class="flex justify-between text-slate-300"><span>Priority</span><span>{detailView.item.priority}</span></div>
              {/if}
              {#if detailView.item.impact}
                <div class="flex justify-between text-slate-300"><span>Impact</span><span>{detailView.item.impact}</span></div>
              {/if}
              {#if detailView.item.analysisStatus}
                <div class="flex justify-between text-slate-300"><span>Analysis</span><span>{detailView.item.analysisStatus}</span></div>
              {/if}
              {#if detailView.item.progress !== undefined}
                <div>
                  <div class="flex justify-between text-slate-300">
                    <span>Progress</span>
                    <span>{detailView.item.progress}%</span>
                  </div>
                  <div class="mt-2 h-2 rounded-full bg-slate-800">
                    <div class="h-2 rounded-full bg-gradient-to-r from-indigo-400 to-emerald-400" style={`width: ${detailView.item.progress}%`}></div>
                  </div>
                </div>
              {/if}
            </dl>
          </div>
          <div class="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <h4 class="text-xs uppercase tracking-wide text-slate-400">Deadlines</h4>
            <p class="mt-3 text-sm text-slate-300">Keep timelines aligned. Auto reminders surface when reviews slip.</p>
            <button class="mt-4 inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:border-indigo-500/40 hover:text-indigo-200">
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l3 3" />
              </svg>
              Schedule reminder
            </button>
          </div>
        </aside>
      </div>
    </div>
  </div>
{/if}

{#if metricHistoryModal.open}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur">
    <div class="w-full max-w-lg rounded-3xl border border-slate-800 bg-slate-950/95 p-6">
      <div class="flex items-start justify-between">
        <div>
          <h3 class="text-lg font-semibold text-slate-100">{metricHistoryModal.metric.title}</h3>
          <p class="text-sm text-slate-400">Trend history across the last {metricHistoryModal.window} days.</p>
        </div>
        <button class="rounded-full border border-slate-700 p-1 text-slate-400 hover:text-white" on:click={closeMetricHistory} aria-label="Close metric history">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="m6 18 12-12M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="mt-6 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
        <div class="text-3xl font-semibold text-indigo-100">{metricHistoryModal.metric.value}</div>
        <div class="text-xs text-slate-400">{metricHistoryModal.metric.delta}</div>
        <svg class="mt-6 h-40 w-full" viewBox="0 0 400 160" preserveAspectRatio="none">
          <polyline
            fill="none"
            stroke="#6366f1"
            stroke-width="4"
            points={metricHistoryModal.metric.trend
              .map((value, index, array) => {
                const x = (index / (array.length - 1)) * 400;
                const min = Math.min(...array);
                const max = Math.max(...array);
                const y = 160 - ((value - min) / (max - min || 1)) * 140 - 10;
                return `${x},${y}`;
              })
              .join(' ')}
          />
        </svg>
        <div class="mt-4 flex items-center justify-end gap-2 text-xs text-slate-400">
          {#each [7, 30, 90] as window}
            <button class={`rounded-full px-3 py-1 ${metricHistoryModal.window === window ? 'bg-indigo-500 text-slate-950 font-semibold' : 'border border-slate-700 hover:border-indigo-400/40 hover:text-indigo-200'}`} on:click={() => (metricHistoryModal = { ...metricHistoryModal, window })}>
              {window}d
            </button>
          {/each}
        </div>
      </div>
    </div>
  </div>
{/if}

{#if createModals.expectation}
  <Modal title="Add Expectation" on:close={() => closeCreateModal('expectation')}>
    <form class="space-y-4" on:submit|preventDefault={addExpectation}>
      <FormField label="Title">
        <input class="form-input" placeholder="Expectation title" value={newExpectation.title} on:input={(event) => (newExpectation.title = event.target.value)} required />
      </FormField>
      <FormField label="Owner">
        <input class="form-input" placeholder="Owner" value={newExpectation.owner} on:input={(event) => (newExpectation.owner = event.target.value)} />
      </FormField>
      <FormField label="Priority">
        <select class="form-input" value={newExpectation.priority} on:change={(event) => (newExpectation.priority = event.target.value)}>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
      </FormField>
      <FormField label="Domain">
        <input class="form-input" placeholder="Domain" value={newExpectation.domain} on:input={(event) => (newExpectation.domain = event.target.value)} />
      </FormField>
      <FormField label="Summary">
        <textarea class="form-textarea" rows="3" placeholder="Describe the expectation" value={newExpectation.summary} on:input={(event) => (newExpectation.summary = event.target.value)}></textarea>
      </FormField>
      <div class="flex justify-end gap-2">
        <button type="button" class="btn-secondary" on:click={() => closeCreateModal('expectation')}>Cancel</button>
        <button type="submit" class="btn-primary">Add Expectation</button>
      </div>
    </form>
  </Modal>
{/if}

{#if createModals.requirement}
  <Modal title="Add Requirement" on:close={() => closeCreateModal('requirement')}>
    <form class="space-y-4" on:submit|preventDefault={addRequirement}>
      <FormField label="Title">
        <input class="form-input" placeholder="Requirement title" value={newRequirement.title} on:input={(event) => (newRequirement.title = event.target.value)} required />
      </FormField>
      <FormField label="Assignee">
        <input class="form-input" placeholder="Assignee" list="assignee-options" value={newRequirement.assignee} on:input={(event) => (newRequirement.assignee = event.target.value)} />
        <datalist id="assignee-options">
          {#each teamMembers as member}
            <option value={member.name}></option>
          {/each}
        </datalist>
      </FormField>
      <FormField label="Priority">
        <select class="form-input" value={newRequirement.priority} on:change={(event) => (newRequirement.priority = event.target.value)}>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
      </FormField>
      <FormField label="Source" description="Link to an existing expectation">
        <input class="form-input" placeholder="Linked expectation" list="expectation-options" value={newRequirement.source} on:input={(event) => (newRequirement.source = event.target.value)} />
        <datalist id="expectation-options">
          {#each expectations as expectation}
            <option value={expectation.id}>{expectation.title}</option>
          {/each}
        </datalist>
      </FormField>
      <FormField label="Summary">
        <textarea class="form-textarea" rows="3" placeholder="Describe the requirement" value={newRequirement.summary} on:input={(event) => (newRequirement.summary = event.target.value)}></textarea>
      </FormField>
      <div class="flex justify-end gap-2">
        <button type="button" class="btn-secondary" on:click={() => closeCreateModal('requirement')}>Cancel</button>
        <button type="submit" class="btn-primary">Add Requirement</button>
      </div>
    </form>
  </Modal>
{/if}

{#if createModals.changeRequest}
  <Modal title="Add Change Request" on:close={() => closeCreateModal('changeRequest')}>
    <form class="space-y-4" on:submit|preventDefault={addChangeRequest}>
      <FormField label="Title">
        <input class="form-input" placeholder="Change Request title" value={newChangeRequest.title} on:input={(event) => (newChangeRequest.title = event.target.value)} required />
      </FormField>
      <FormField label="Owner">
        <input class="form-input" placeholder="Owner" value={newChangeRequest.owner} on:input={(event) => (newChangeRequest.owner = event.target.value)} />
      </FormField>
      <FormField label="Priority">
        <select class="form-input" value={newChangeRequest.priority} on:change={(event) => (newChangeRequest.priority = event.target.value)}>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
      </FormField>
      <FormField label="Linked Requirement">
        <select class="form-input" value={newChangeRequest.linkedRequirement} on:change={(event) => (newChangeRequest.linkedRequirement = event.target.value)}>
          <option value="">Select requirement</option>
          {#each requirements as requirement}
            <option value={requirement.id}>{requirement.id} · {requirement.title}</option>
          {/each}
        </select>
      </FormField>
      <div class="grid grid-cols-2 gap-4">
        <FormField label="Impact">
          <select class="form-input" value={newChangeRequest.impact} on:change={(event) => (newChangeRequest.impact = event.target.value)}>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </FormField>
        <FormField label="Analysis Status">
          <select class="form-input" value={newChangeRequest.analysisStatus} on:change={(event) => (newChangeRequest.analysisStatus = event.target.value)}>
            <option>Not started</option>
            <option>In progress</option>
            <option>Complete</option>
          </select>
        </FormField>
      </div>
      <FormField label="Summary">
        <textarea class="form-textarea" rows="3" placeholder="Describe the requested change" value={newChangeRequest.summary} on:input={(event) => (newChangeRequest.summary = event.target.value)}></textarea>
      </FormField>
      <div class="flex justify-end gap-2">
        <button type="button" class="btn-secondary" on:click={() => closeCreateModal('changeRequest')}>Cancel</button>
        <button type="submit" class="btn-primary">Add Change Request</button>
      </div>
    </form>
  </Modal>
{/if}

{#if notifyModalOpen}
  <Modal title="Notify Project Manager" on:close={() => (notifyModalOpen = false)}>
    <form class="space-y-4" on:submit|preventDefault={submitNotify}>
      <FormField label="Message" description="Explain the lifecycle concern you discovered.">
        <textarea class="form-textarea" rows="4" placeholder="Tell the project manager what you need" value={notifyComment} on:input={(event) => (notifyComment = event.target.value)}></textarea>
      </FormField>
      <div class="flex justify-end gap-2">
        <button type="button" class="btn-secondary" on:click={() => (notifyModalOpen = false)}>Cancel</button>
        <button type="submit" class="btn-primary">Send notification</button>
      </div>
    </form>
  </Modal>
{/if}
