<script>
  import { createEventDispatcher } from 'svelte';
  import Sparkline from './Sparkline.svelte';

  export let projectMetrics = [];
  export let activityLog = [];
  export let bottlenecks = [];
  export let summaryCounts = { expectations: 0, requirements: 0, changeRequests: 0 };
  export let activityFilter = 'All';
  export let severityBadge = () => '';

  const dispatch = createEventDispatcher();

  const cards = [
    { id: 'expectations', title: 'Expectations', key: 'expectations' },
    { id: 'requirements', title: 'Requirements', key: 'requirements' },
    { id: 'changeRequests', title: 'Change Requests', key: 'changeRequests' }
  ];

  const activityTypes = ['All', 'Expectation', 'Requirement', 'Change Request', 'Conversion', 'Status', 'Implementation', 'Link', 'Alert'];

  $: filteredActivity = activityFilter === 'All' ? activityLog : activityLog.filter((item) => item.type === activityFilter);
</script>

<section class="space-y-8 px-4 py-6 md:px-6">
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
    {#each cards as card}
      <div class="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-slate-100">{card.title}</h3>
          <button class="rounded-full bg-indigo-500/10 px-3 py-1 text-xs text-indigo-200 hover:bg-indigo-500/20" on:click={() => dispatch('navigate', card.id)}>
            View all
          </button>
        </div>
        <div class="mt-4 flex items-end justify-between">
          <div>
            <div class="text-3xl font-semibold text-white">{summaryCounts[card.key]}</div>
            <div class="mt-1 text-xs text-slate-400">Lifecycle items in focus</div>
          </div>
          <Sparkline values={[4, 6, 5, 7, 9, 8, 10]} accent={card.id} />
        </div>
      </div>
    {/each}
  </div>

  <div class="grid grid-cols-1 gap-6 xl:grid-cols-[2fr,1fr]">
    <div class="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
      <header class="flex flex-wrap items-center gap-4">
        <div>
          <h3 class="text-base font-semibold text-slate-100">Activity stream</h3>
          <p class="text-xs text-slate-400">Track key lifecycle moves across expectations, requirements, and change requests.</p>
        </div>
        <div class="ml-auto flex flex-wrap gap-2 text-xs">
          {#each activityTypes as type}
            <button class={`rounded-full px-3 py-1 transition ${activityFilter === type ? 'bg-indigo-500 text-slate-950 font-semibold' : 'border border-slate-700 text-slate-300 hover:border-indigo-400/40 hover:text-white'}`} on:click={() => (activityFilter = type)}>
              {type}
            </button>
          {/each}
        </div>
      </header>
      <ol class="mt-6 space-y-4">
        {#each filteredActivity as event}
          <li class="flex gap-3">
            <div class="relative">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500/10 text-sm text-indigo-200">{event.type.charAt(0)}</div>
            </div>
            <div class="flex-1 rounded-2xl border border-slate-800/70 bg-slate-900/60 p-4">
              <div class="flex flex-wrap items-center gap-2 text-sm text-slate-100">
                <span>{event.action}</span>
                <span class="rounded-full bg-slate-800 px-2 py-0.5 text-[11px] text-slate-400">{event.type}</span>
              </div>
              <div class="mt-1 text-xs text-slate-500">{event.timestamp} • {event.author}</div>
            </div>
          </li>
        {:else}
          <li class="rounded-2xl border border-dashed border-slate-700 p-8 text-center text-sm text-slate-400">No events yet for this filter.</li>
        {/each}
      </ol>
    </div>
    <div class="space-y-6">
      <div class="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 class="text-base font-semibold text-slate-100">Bottlenecks</h3>
        <ul class="mt-4 space-y-3">
          {#each bottlenecks as issue}
            <li class="rounded-2xl border border-slate-800/70 bg-slate-900/60 p-4">
              <div class="flex items-center justify-between text-sm text-slate-100">
                <span>{issue.title}</span>
                <span class={`rounded-full px-3 py-1 text-[11px] uppercase tracking-wide ${severityBadge(issue.severity)}`}>{issue.severity}</span>
              </div>
              <p class="mt-2 text-xs text-slate-400">{issue.description}</p>
              <button class="mt-3 inline-flex items-center gap-2 rounded-full bg-rose-500/10 px-3 py-1.5 text-xs text-rose-200 hover:bg-rose-500/20" on:click={() => dispatch('navigate', issue.cta.target)}>
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
                </svg>
                {issue.cta.label}
              </button>
            </li>
          {/each}
        </ul>
      </div>

      <div class="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
        <header class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold text-slate-100">Project metrics</h3>
            <p class="text-xs text-slate-400">Pulse on lifecycle health. Open history to inspect trend lines.</p>
          </div>
        </header>
        <div class="mt-4 space-y-4">
          {#each projectMetrics as metric}
            <div class="rounded-2xl border border-slate-800/70 bg-slate-900/60 p-4">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-sm font-semibold text-slate-100">{metric.title}</div>
                  <div class="mt-1 text-xs text-slate-400">{metric.delta}</div>
                </div>
                <div class="text-2xl font-semibold text-indigo-100">{metric.value}</div>
              </div>
              <Sparkline values={metric.trend} accent="metric" />
              <button class="mt-3 inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:border-indigo-400/40 hover:text-indigo-200" on:click={() => dispatch('openMetric', metric)}>
                See history
              </button>
            </div>
          {/each}
        </div>
      </div>
    </div>
  </div>
</section>

