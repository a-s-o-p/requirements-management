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

  $: statusOptions = Array.from(new Set(allItems.map((item) => item.status)));
  $: priorityOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.priority)))];
  $: domainOptions = ['All', ...Array.from(new Set(allItems.map((item) => item.domain)))];

  function updateFilters(patch) {
    dispatch('updateFilters', { ...filters, ...patch });
  }

  function toggleStatus(status) {
    const updated = new Set(filters.status);
    if (updated.has(status)) {
      updated.delete(status);
    } else {
      updated.add(status);
    }
    updateFilters({ status: updated });
  }

  function requestSort(field) {
    dispatch('updateSort', field);
  }

  function actionIcon(name) {
    if (name === 'view') return 'M12 6v12m6-6H6';
    if (name === 'edit') return 'M16.862 4.487a2.25 2.25 0 1 1 3.182 3.182L7.5 20.213l-4.5.75.75-4.5 13.112-11.976z';
    if (name === 'delete') return 'M6 7h12m-9 4v6m6-6v6M9 7l.867-2.6A2 2 0 0 1 11.786 3h.428a2 2 0 0 1 1.919 1.4L15 7m-9 0h12m-1 0v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V7h12z';
    if (name === 'analyze') return 'M3 8l9-6 9 6v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8zm9 9l3-3m0 0l3 3m-3-3v6';
    if (name === 'link') return 'M8 7h.01M21 13l-4 4a4 4 0 0 1-5.657 0l-1.172-1.172m2.829-2.829 1.172 1.172a2 2 0 0 0 2.829 0l4-4a2 2 0 0 0-2.829-2.829l-1.172 1.172m-6 6L9 17a2 2 0 0 1-2.828 0l-4-4a2 2 0 0 1 2.828-2.828l1.172 1.172';
    return '';
  }
</script>

<section class="space-y-6 px-4 py-6 md:px-6">
  <header class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-semibold text-white">Expectations</h1>
      <p class="text-sm text-slate-400">Filter, triage, and promote expectations into requirements.</p>
    </div>
    <button class="inline-flex items-center gap-2 rounded-full bg-indigo-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-indigo-400" on:click={() => dispatch('create')}>
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m6-6H6" />
      </svg>
      Add Expectation
    </button>
  </header>

  <div class="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-6">
      <div class="lg:col-span-2">
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="expectation-search">Search</label>
        <input
          id="expectation-search"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
          placeholder="Title or text"
          value={filters.search}
          on:input={(event) => updateFilters({ search: event.target.value })}
        />
      </div>
      <div>
        <p class="text-xs font-semibold uppercase tracking-wide text-slate-300">Status</p>
        <div class="mt-2 flex flex-wrap gap-2">
          {#each statusOptions as status}
            <button class={`rounded-full px-3 py-1 text-xs transition ${filters.status.has(status) ? 'bg-indigo-500 text-slate-950 font-semibold' : 'border border-slate-700 text-slate-300 hover:border-indigo-400/40 hover:text-white'}`} on:click={() => toggleStatus(status)}>
              {status}
            </button>
          {/each}
        </div>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="expectation-priority">Priority</label>
        <select
          id="expectation-priority"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
          value={filters.priority}
          on:change={(event) => updateFilters({ priority: event.target.value })}
        >
          {#each priorityOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div>
        <label class="text-xs font-semibold uppercase tracking-wide text-slate-300" for="expectation-domain">Domain</label>
        <select
          id="expectation-domain"
          class="mt-2 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
          value={filters.domain}
          on:change={(event) => updateFilters({ domain: event.target.value })}
        >
          {#each domainOptions as option}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </div>
      <div class="lg:col-span-2">
        <p id="expectation-ice-label" class="text-xs font-semibold uppercase tracking-wide text-slate-300">ICE score</p>
        <div class="mt-2 flex items-center gap-3 text-xs text-slate-300" role="group" aria-labelledby="expectation-ice-label">
          <input type="number" min="0" max="30" class="w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/30" value={filters.iceMin} on:input={(event) => updateFilters({ iceMin: Number(event.target.value) })} />
          <span>to</span>
          <input type="number" min="0" max="30" class="w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/30" value={filters.iceMax} on:input={(event) => updateFilters({ iceMax: Number(event.target.value) })} />
        </div>
      </div>
    </div>
    <div class="mt-4 flex justify-between text-xs text-slate-400">
      <span>{items.length} expectations shown</span>
      <button class="rounded-full px-3 py-1 text-xs text-slate-300 hover:bg-slate-800/60" on:click={() => dispatch('updateFilters', { search: '', status: new Set(), priority: 'All', domain: 'All', iceMin: 0, iceMax: 30 })}>
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
          <SortableHeader label="Domain" field="domain" {sort} on:toggle={requestSort} />
          <SortableHeader label="ICE Score" field="iceScore" {sort} on:toggle={requestSort} />
          <th class="px-4 py-2 text-left text-xs uppercase tracking-wide text-slate-400">Flags</th>
          <th class="px-4 py-2 text-right text-xs uppercase tracking-wide text-slate-400">Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each items as item}
          <tr class="rounded-2xl border border-slate-800/70 bg-slate-900/60">
            <td class="rounded-l-2xl px-4 py-3 align-top">
              <button class="text-left font-semibold text-slate-100 hover:text-indigo-200" on:click={() => dispatch('view', item)}>
                {item.id} · {item.title}
              </button>
              <p class="mt-1 text-xs text-slate-400">{item.summary}</p>
            </td>
            <td class="px-4 py-3 align-top">
              <span class={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs ${statusBadge(item.status)}`} title={item.status}>{item.status}</span>
            </td>
            <td class="px-4 py-3 align-top">
              <span class={`rounded-full px-3 py-1 text-xs ${priorityBadge(item.priority)}`}>{item.priority}</span>
            </td>
            <td class="px-4 py-3 align-top text-xs text-slate-300">{item.domain}</td>
            <td class="px-4 py-3 align-top text-xs text-slate-300">{item.iceScore}</td>
            <td class="px-4 py-3 align-top text-xs">
              <div class="flex flex-wrap gap-2">
                {#each item.flags as flag}
                  <span class="rounded-full bg-rose-500/10 px-2 py-1 text-[11px] text-rose-200" title={flag}>{flag}</span>
                {:else}
                  <span class="text-slate-500">—</span>
                {/each}
              </div>
            </td>
            <td class="rounded-r-2xl px-4 py-3 align-top">
              <div class="flex justify-end gap-2">
                {#each ['view', 'edit', 'delete', 'analyze', 'link'] as action}
                  <button class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800/80 bg-slate-950/60 text-slate-300 transition hover:border-indigo-400/40 hover:text-indigo-200" title={action === 'link' ? 'Link to Requirements' : action.charAt(0).toUpperCase() + action.slice(1)} on:click={() => {
                    if (action === 'view') dispatch('view', item);
                    if (action === 'link') dispatch('link', item);
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
              Nothing here yet. <button class="text-indigo-300 underline" on:click={() => dispatch('create')}>Add Expectation</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</section>

