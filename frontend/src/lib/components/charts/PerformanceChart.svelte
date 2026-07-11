<script lang="ts">
  import { Chart } from 'chart.js/auto'
  import type { SerieRentabilidade } from '../../api/carteira'
  import { fmtPct, fmtMesAno } from '../../utils/format'

  let { serie }: { serie: SerieRentabilidade | null } = $props()

  let canvas: HTMLCanvasElement
  let chart: Chart | undefined

  $effect(() => {
    Chart.defaults.font.family = "'IBM Plex Sans', sans-serif"
    Chart.defaults.color = '#6B7A8C'
    chart = new Chart(canvas, {
      type: 'line',
      data: { labels: [], datasets: [] },
      options: {
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              pointStyle: 'line',
              boxWidth: 24,
              padding: 16,
              font: { size: 12 },
            },
          },
          tooltip: {
            callbacks: { label: (c) => ` ${c.dataset.label}: ${fmtPct(c.parsed.y ?? 0)}` },
          },
        },
        scales: {
          y: { ticks: { callback: (v) => v + '%' }, grid: { color: '#EDF1F6' } },
          x: { grid: { display: false } },
        },
      },
    })
    return () => chart?.destroy()
  })

  $effect(() => {
    if (!chart || !serie) return
    chart.data.labels = serie.datas.map(fmtMesAno)
    chart.data.datasets = [
      {
        label: 'Carteira',
        data: serie.carteira,
        borderColor: '#1E3A5F',
        backgroundColor: 'rgba(30,58,95,.06)',
        fill: true,
        borderWidth: 2.5,
        pointRadius: 0,
        pointHoverRadius: 4,
        tension: 0.3,
      },
      {
        label: 'CDI',
        data: serie.cdi,
        borderColor: '#8FA3BC',
        borderDash: [5, 4],
        borderWidth: 1.8,
        pointRadius: 0,
        tension: 0.3,
      },
      {
        label: 'Ibovespa',
        data: serie.ibovespa,
        borderColor: '#B98A2F',
        borderWidth: 1.8,
        pointRadius: 0,
        tension: 0.3,
      },
    ]
    chart.update()
  })
</script>

<div class="chart-box">
  <canvas
    bind:this={canvas}
    aria-label="Gráfico de linha da rentabilidade acumulada da carteira, CDI e Ibovespa"
  ></canvas>
</div>
