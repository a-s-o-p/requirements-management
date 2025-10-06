<script>
  export let label;
  export let description = '';
  export let forId;
</script>

<label class="block text-sm">
  <span class="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-300" for={forId}>{label}</span>
  <slot></slot>
  {#if description}
    <p class="mt-1 text-xs text-slate-500">{description}</p>
  {/if}
</label>
