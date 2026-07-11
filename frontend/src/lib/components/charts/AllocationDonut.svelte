<script lang="ts">
  import { Chart } from 'chart.js/auto'
  import type { Posicao } from '../../api/posicoes'
  import { fmtBRL, classeLabel } from '../../utils/format'

  let { posicoes }: { posicoes: Posicao[] } = $props()

  let canvas: HTMLCanvasElement
  let chart: Chart<'doughnut'> | undefined

  $effect(() => {
    chart = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: [],
        datasets: [
          {
            data: [],
            backgroundColor: ['#1E3A5F', '#B98A2F', '#8FA3BC', '#5E7AA0'],
            borderWidth: 2,
            borderColor: '#fff',
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { usePointStyle: true, boxWidth: 8, padding: 14, font: { size: 12 } },
          },
          tooltip: { callbacks: { label: (c) => ` ${c.label}: ${fmtBRL(c.parsed)}` } },
        },
      },
    })
    return () => chart?.destroy()
  })

  $effect(() => {
    if (!chart) return
    const porClasse: Record<string, number> = {}
    for (const p of posicoes) {
      const rotulo = classeLabel(p.classe)
      porClasse[rotulo] = (porClasse[rotulo] ?? 0) + Number(p.valor_mercado ?? 0)
    }
    chart.data.labels = Object.keys(porClasse)
    chart.data.datasets[0].data = Object.values(porClasse)
    chart.update()
  })
</script>

<div class="chart-box small">
  <canvas
    bind:this={canvas}
    aria-label="Gráfico de alocação da carteira por classe de ativo"
  ></canvas>
</div>
