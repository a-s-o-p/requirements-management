<script>
  import { createEventDispatcher } from 'svelte';

  export let label;
  export let field;
  export let sort = { field: '', direction: 'asc' };

  const dispatch = createEventDispatcher();

  $: direction = sort.field === field ? sort.direction : null;
  $: icon = direction === 'asc' ? 'M5 15l7-7 7 7' : direction === 'desc' ? 'M19 9l-7 7-7-7' : 'M4 9h16M4 15h16';
</script>

<th class="px-4 py-2 text-left text-xs uppercase tracking-wide text-slate-400">
  <button class="flex w-full items-center gap-2" on:click={() => dispatch('toggle', field)}>
    <span>{label}</span>
    <span class="flex h-6 w-3 cursor-col-resize items-center justify-center rounded bg-slate-800/60"></span>
    <svg class="h-4 w-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path stroke-linecap="round" stroke-linejoin="round" d={icon} />
    </svg>
  </button>
</th>
