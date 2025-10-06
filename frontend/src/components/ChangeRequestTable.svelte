<script>
  import { createEventDispatcher } from 'svelte';
  import SortableHeader from './SortableHeader.svelte';

  export let items = [];
  export let allItems = [];
  export let filters;
  export let sort;
  export let statusBadge = () => '';
  export let priorityBadge = () => '';
  export let impactColors = { High: 'bg-rose-500/20 text-rose-100', Medium: 'bg-amber-500/20 text-amber-100', Low: 'bg-sky-500/20 text-sky-100' };

  const dispatch = createEventDispatcher();

  $: statusOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.status)))];
  $: priorityOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.priority)))];
  $: linkedRequirementOptions = ['All', ...Array.from(new Set(allItems.flatMap((item) => item.linkedRequirements || [])))];
  $: analysisOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.analysisStatus)))];

  function updateFilters(patch) {
    dispatch('updateFilters', { ...filters, ...patch });
  }

  function requestSort(field) {
    dispatch('updateSort', field);
  }

  function actionIcon(name) {
    if (name === 'view') return 'M12 6v12m6-6H6';
    if (name === 'edit') return 'M16.862 4.487a2.25 2.25 0 1 1 3.182 3.182L7.5 20.213l-4.5.75.75-4.5 13.112-11.976z';
    if (name === 'delete') return 'M6 7h12m-9 4v6m6-6v6M9 7l.867-2.6A2 2 0 0 1 11.786 3h.428a2 2 0 0 1 1.919 1.4L15 7m-9 0h12m-1 0v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V7h12z';
    if (name === 'analyze') return 'M3 8l9-6 9 6v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8zm9 9l3-3m0 0l3 3m-3-3v6';
    if (name === 'implement') return 'M4.5 12.75l6 6 9-13.5';
    return '';
  }
</script>

<section class="space-y-6 px-4 py-6 md:px-6">
  <header class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-semibold text-white">Change Requests</h1>
      <p class="text-sm text-slate-400">Monitor impact, analysis, and implementation decisions.</p>
    </div>
    <button class="inline-flex items-center gap-2 rounded-full bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-300" on:click={() => dispatch('create')}>
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m6-6H6" />
      </svg>
      Add Change Request
    </button>
  </header>

  <div class="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-6">
      <div class="lg:col-span-2">
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="change-search">Search</label>
        <input
          id="change-search"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/30"
          placeholder="Title"
          value={filters.search}
          on:input={(event) => updateFilters({ search: event.target.value })}
        />
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="change-status">Status</label>
        <select
          id="change-status"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/30"
          value={filters.status}
          on:change={(event) => updateFilters({ status: event.target.value })}
        >
          {#each statusOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="change-priority">Priority</label>
        <select
          id="change-priority"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/30"
          value={filters.priority}
          on:change={(event) => updateFilters({ priority: event.target.value })}
        >
          {#each priorityOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="change-linked">Linked Requirement</label>
        <select
          id="change-linked"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/30"
          value={filters.linkedRequirement}
          on:change={(event) => updateFilters({ linkedRequirement: event.target.value })}
        >
          {#each linkedRequirementOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="change-impact">Impact</label>
        <select
          id="change-impact"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/30"
          value={filters.impact}
          on:change={(event) => updateFilters({ impact: event.target.value })}
        >
          {#each ['All', 'High', 'Medium', 'Low'] as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="change-analysis">Analysis status</label>
        <select
          id="change-analysis"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/30"
          value={filters.analysisStatus}
          on:change={(event) => updateFilters({ analysisStatus: event.target.value })}
        >
          {#each analysisOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
    </div>
    <div class="mt-4 flex justify-between text-xs text-slate-400">
      <span>{items.length} change requests shown</span>
      <button class="rounded-full px-3 py-1 text-xs text-slate-300 hover:bg-slate-800/60" on:click={() => dispatch('updateFilters', { search: '', status: 'All', priority: 'All', linkedRequirement: 'All', impact: 'All', analysisStatus: 'All' })}>
        Reset filters
      </button>
    </div>
  </div>

  <div class="overflow-x-auto">
    <table class="min-w-full border-separate border-spacing-y-2 text-sm text-slate-200">
      <thead>
        <tr>
          <SortableHeader label="Title" field="title" {sort} on:toggle={requestSort} />
          <SortableHeader label="Status" field="status" {sort} on:toggle={requestSort} />
          <SortableHeader label="Priority" field="priority" {sort} on:toggle={requestSort} />
          <SortableHeader label="Linked Requirements" field="linkedRequirements" {sort} on:toggle={requestSort} />
          <SortableHeader label="Impact" field="impact" {sort} on:toggle={requestSort} />
          <SortableHeader label="Analysis" field="analysisStatus" {sort} on:toggle={requestSort} />
          <th class="px-4 py-2 text-right text-xs uppercase tracking-wide text-slate-400">Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each items as item}
          <tr class="rounded-2xl border border-slate-800/70 bg-slate-900/60">
            <td class="rounded-l-2xl px-4 py-3 align-top">
              <button class="text-left font-semibold text-slate-100 hover:text-amber-200" on:click={() => dispatch('view', item)}>
                {item.id} · {item.title}
              </button>
              <p class="mt-1 text-xs text-slate-400">Submitted {item.submitted}</p>
            </td>
            <td class="px-4 py-3 align-top">
              <span class={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs ${statusBadge(item.status)}`}>{item.status}</span>
            </td>
            <td class="px-4 py-3 align-top">
              <span class={`rounded-full px-3 py-1 text-xs ${priorityBadge(item.priority)}`}>{item.priority}</span>
            </td>
            <td class="px-4 py-3 align-top text-xs text-slate-300">
              <div class="flex flex-wrap gap-2">
                {#each item.linkedRequirements as req}
                  <span class="rounded-full bg-slate-800 px-2 py-1 text-[11px] text-slate-200">{req}</span>
                {:else}
                  <span class="text-slate-500">—</span>
                {/each}
              </div>
            </td>
            <td class="px-4 py-3 align-top text-xs">
              <span class={`rounded-full px-3 py-1 text-xs ${impactColors[item.impact] || 'bg-slate-800 text-slate-200'}`}>{item.impact}</span>
            </td>
            <td class="px-4 py-3 align-top text-xs text-slate-300">{item.analysisStatus}</td>
            <td class="rounded-r-2xl px-4 py-3 align-top">
              <div class="flex justify-end gap-2">
                {#each ['view', 'edit', 'delete', 'analyze', 'implement'] as action}
                  <button class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800/80 bg-slate-950/60 text-slate-300 transition hover:border-amber-400/40 hover:text-amber-200" title={action === 'implement' ? 'Implement' : action.charAt(0).toUpperCase() + action.slice(1)} on:click={() => {
                    if (action === 'view') dispatch('view', item);
                    if (action === 'implement') dispatch('implement', item);
                  }}>
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d={actionIcon(action)} />
                    </svg>
                  </button>
                {/each}
              </div>
            </td>
          </tr>
        {:else}
          <tr>
            <td colspan="7" class="rounded-2xl border border-dashed border-slate-700 bg-slate-900/50 p-12 text-center text-sm text-slate-400">
              No change requests yet. <button class="text-amber-300 underline" on:click={() => dispatch('create')}>Add Change Request</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</section>
