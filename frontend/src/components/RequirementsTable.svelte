<script>
  import { createEventDispatcher } from 'svelte';
  import SortableHeader from './SortableHeader.svelte';

  export let items = [];
  export let allItems = [];
  export let filters;
  export let sort;
  export let statusBadge = () => '';
  export let priorityBadge = () => '';

  const dispatch = createEventDispatcher();

  $: statusOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.status)))];
  $: priorityOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.priority)))];
  $: assigneeOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.assignee)))];
  $: sourceOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.source)))];

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
    if (name === 'change') return 'M4 7v6a5 5 0 0 0 10 0V7m6 10v-6a5 5 0 1 0-10 0v6';
    return '';
  }
</script>

<section class="space-y-6 px-4 py-6 md:px-6">
  <header class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-semibold text-white">Requirements</h1>
      <p class="text-sm text-slate-400">Assess readiness, ownership, and progress to keep delivery aligned.</p>
    </div>
    <button class="inline-flex items-center gap-2 rounded-full bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-300" on:click={() => dispatch('create')}>
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m6-6H6" />
      </svg>
      Add Requirement
    </button>
  </header>

  <div class="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-6">
      <div class="lg:col-span-2">
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="requirement-search">Search</label>
        <input
          id="requirement-search"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30"
          placeholder="Title"
          value={filters.search}
          on:input={(event) => updateFilters({ search: event.target.value })}
        />
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="requirement-status">Status</label>
        <select
          id="requirement-status"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30"
          value={filters.status}
          on:change={(event) => updateFilters({ status: event.target.value })}
        >
          {#each statusOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="requirement-priority">Priority</label>
        <select
          id="requirement-priority"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30"
          value={filters.priority}
          on:change={(event) => updateFilters({ priority: event.target.value })}
        >
          {#each priorityOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="requirement-assignee">Assignee</label>
        <select
          id="requirement-assignee"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30"
          value={filters.assignee}
          on:change={(event) => updateFilters({ assignee: event.target.value })}
        >
          {#each assigneeOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div>
        <p id="requirement-progress-label" class="text-xs font-semibold uppercase tracking-wide text-slate-300">Progress</p>
        <div class="mt-2 flex items-center gap-3 text-xs text-slate-300" role="group" aria-labelledby="requirement-progress-label">
          <input type="number" min="0" max="100" class="w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30" value={filters.progressMin} on:input={(event) => updateFilters({ progressMin: Number(event.target.value) })} />
          <span>to</span>
          <input type="number" min="0" max="100" class="w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30" value={filters.progressMax} on:input={(event) => updateFilters({ progressMax: Number(event.target.value) })} />
        </div>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="requirement-source">Source</label>
        <select
          id="requirement-source"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-400/30"
          value={filters.source}
          on:change={(event) => updateFilters({ source: event.target.value })}
        >
          {#each sourceOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
    </div>
    <div class="mt-4 flex justify-between text-xs text-slate-400">
      <span>{items.length} requirements shown</span>
      <button class="rounded-full px-3 py-1 text-xs text-slate-300 hover:bg-slate-800/60" on:click={() => dispatch('updateFilters', { search: '', status: 'All', priority: 'All', assignee: 'All', progressMin: 0, progressMax: 100, source: 'All' })}>
        Reset filters
      </button>
    </div>
  </div>

  <div class="overflow-x-auto">
    <table class="min-w-full border-separate border-spacing-y-2 text-sm text-slate-200">
      <thead>
        <tr>
          <SortableHeader label="Requirement" field="title" {sort} on:toggle={requestSort} />
          <SortableHeader label="Status" field="status" {sort} on:toggle={requestSort} />
          <SortableHeader label="Priority" field="priority" {sort} on:toggle={requestSort} />
          <SortableHeader label="Assignee" field="assignee" {sort} on:toggle={requestSort} />
          <SortableHeader label="Progress" field="progress" {sort} on:toggle={requestSort} />
          <SortableHeader label="Source" field="source" {sort} on:toggle={requestSort} />
          <th class="px-4 py-2 text-right text-xs uppercase tracking-wide text-slate-400">Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each items as item}
          <tr class="rounded-2xl border border-slate-800/70 bg-slate-900/60">
            <td class="rounded-l-2xl px-4 py-3 align-top">
              <button class="text-left font-semibold text-slate-100 hover:text-emerald-200" on:click={() => dispatch('view', item)}>
                {item.id} · {item.title}
              </button>
              <p class="mt-1 text-xs text-slate-400">Updated {item.lastUpdated}</p>
            </td>
            <td class="px-4 py-3 align-top">
              <span class={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs ${statusBadge(item.status)}`}>{item.status}</span>
            </td>
            <td class="px-4 py-3 align-top">
              <span class={`rounded-full px-3 py-1 text-xs ${priorityBadge(item.priority)}`}>{item.priority}</span>
            </td>
            <td class="px-4 py-3 align-top text-xs text-slate-300">{item.assignee}</td>
            <td class="px-4 py-3 align-top text-xs">
              <div class="flex items-center justify-between text-slate-300">
                <span>{item.progress}%</span>
              </div>
              <div class="mt-2 h-2 rounded-full bg-slate-800">
                <div class="h-2 rounded-full bg-gradient-to-r from-emerald-300 to-emerald-500" style={`width: ${item.progress}%`}></div>
              </div>
            </td>
            <td class="px-4 py-3 align-top text-xs text-slate-300">{item.source}</td>
            <td class="rounded-r-2xl px-4 py-3 align-top">
              <div class="flex justify-end gap-2">
                {#each ['view', 'edit', 'delete', 'analyze', 'change'] as action}
                  <button class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800/80 bg-slate-950/60 text-slate-300 transition hover:border-emerald-400/40 hover:text-emerald-200" title={action === 'change' ? 'Create Change Request' : action.charAt(0).toUpperCase() + action.slice(1)} on:click={() => {
                    if (action === 'view') dispatch('view', item);
                    if (action === 'change') dispatch('changeRequest', item);
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
              No requirements yet. <button class="text-emerald-300 underline" on:click={() => dispatch('create')}>Add Requirement</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</section>
