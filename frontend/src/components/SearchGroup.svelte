<script>
  import { createEventDispatcher } from 'svelte';

  export let label;
  export let items = [];
  export let count = 0;
  export let highlightMatch = (text) => text;

  const dispatch = createEventDispatcher();

  function view(item) {
    dispatch('view', item);
  }
</script>

<section class="mb-4 rounded-2xl border border-slate-800 bg-slate-900/70 p-3">
  <header class="flex items-center justify-between text-xs uppercase tracking-wide text-slate-400">
    <div class="flex items-center gap-2">
      <span>{label}</span>
      <span class="rounded-full bg-slate-800 px-2 py-0.5 text-[11px] text-slate-300">{count}</span>
    </div>
    <button class="rounded-full px-2 py-1 text-[11px] font-medium text-indigo-200 hover:bg-indigo-500/10" on:click={() => dispatch('viewAll')}>
      View all in {label}
    </button>
  </header>
  <ul class="mt-3 space-y-2 text-sm">
    {#each items.slice(0, 5) as item}
      <li>
        <button class="flex w-full items-start gap-3 rounded-xl border border-slate-800/70 bg-slate-900/60 p-3 text-left transition hover:border-indigo-500/40 hover:bg-indigo-500/10" on:click={() => view(item)}>
          <div class="mt-1 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-200">
            {label.charAt(0)}
          </div>
          <div class="flex-1">
            <div class="font-medium text-slate-100" innerHTML={highlightMatch(`${item.id ? `${item.id} · ` : ''}${item.title || item.name || ''}`)}></div>
            <div class="mt-1 text-xs text-slate-400" innerHTML={highlightMatch(item.status ? `${item.status}${item.priority ? ` • ${item.priority}` : ''}` : '')}></div>
            {#if item.summary || item.impactSummary}
              <div class="mt-1 text-xs leading-relaxed text-slate-400" innerHTML={highlightMatch((item.summary || item.impactSummary || '').slice(0, 140) + (item.summary && item.summary.length > 140 ? '…' : ''))}></div>
            {/if}
          </div>
        </button>
      </li>
    {/each}
  </ul>
</section>
