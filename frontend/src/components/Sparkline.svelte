<script>
  export let values = [];
  export let accent = 'metric';

  const hasValues = values.length > 0;
  const min = hasValues ? Math.min(...values) : 0;
  const max = hasValues ? Math.max(...values) : 1;

  $: points = hasValues
    ? values
        .map((value, index) => {
          const x = values.length === 1 ? 50 : (index / (values.length - 1)) * 100;
          const y = values.length === 1 ? 50 : 100 - ((value - min) / (max - min || 1)) * 100;
          return `${x},${y}`;
        })
        .join(' ')
    : '0,50 100,50';

  $: strokeColor =
    accent === 'changeRequests'
      ? '#fb7185'
      : accent === 'requirements'
      ? '#34d399'
      : accent === 'expectations'
      ? '#60a5fa'
      : '#a5b4fc';
</script>

<svg class="mt-4 h-16 w-32" viewBox="0 0 100 100" preserveAspectRatio="none">
  <defs>
    <linearGradient id={'spark-' + accent} x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color={strokeColor} stop-opacity="0.6" />
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0" />
    </linearGradient>
  </defs>
  <polyline fill="none" stroke={strokeColor} stroke-width="2" points={points} />
  <polygon fill={`url(#spark-${accent})`} opacity="0.2" points={`${points} 100,100 0,100`} />
</svg>
