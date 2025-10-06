<script>
  import { createEventDispatcher } from 'svelte';

  export let title;

  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur" role="dialog" aria-modal="true">
  <div class="relative w-full max-w-xl rounded-3xl border border-slate-800 bg-slate-950/95 p-6 shadow-2xl">
    <button class="absolute right-6 top-6 rounded-full border border-slate-700 p-1 text-slate-400 hover:text-white" on:click={close} aria-label="Close dialog">
      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="m6 18 12-12M6 6l12 12" />
      </svg>
    </button>
    <header class="pr-8">
      <h3 class="text-lg font-semibold text-slate-100">{title}</h3>
      <p class="mt-1 text-sm text-slate-400">Fill in the required fields to keep the lifecycle in sync.</p>
    </header>
    <div class="mt-4">
      <slot></slot>
    </div>
  </div>
</div>
