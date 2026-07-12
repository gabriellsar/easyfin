<script lang="ts">
  import { fmtPct, fmtPctAbs, indiceLabel } from '../utils/format'

  let {
    carteira = 0,
    indices = [],
  }: { carteira?: number; indices?: { chave: string; valor: number }[] } = $props()

  const COR_INDICE: Record<string, string> = {
    cdi: '#8FA3BC',
    ibovespa: '#B98A2F',
  }

  let maximo = $derived(Math.max(carteira, ...indices.map((i) => i.valor), 0.001))

  let badge = $derived.by(() => {
    const partes: string[] = []
    const cdi = indices.find((i) => i.chave === 'cdi')
    if (cdi && cdi.valor !== 0) {
      partes.push(`entregou ${fmtPctAbs((carteira / cdi.valor) * 100, 0)} do CDI`)
    }
    const ibov = indices.find((i) => i.chave === 'ibovespa')
    if (ibov) {
      const dif = carteira - ibov.valor
      partes.push(
        dif >= 0
          ? `superou o Ibovespa em ${fmtPctAbs(dif)} p.p.`
          : `ficou ${fmtPctAbs(-dif)} p.p. abaixo do Ibovespa`,
      )
    }
    return partes.length ? `Carteira ${partes.join(' e ')}` : null
  })

  let montado = $state(false)
  $effect(() => {
    const raf = requestAnimationFrame(() => (montado = true))
    return () => cancelAnimationFrame(raf)
  })

  const largura = (valor: number) =>
    montado ? `${((valor / maximo) * 100).toFixed(1)}%` : '0'
</script>

<div class="ruler">
  <div class="ruler-row">
    <div class="ruler-name">Carteira</div>
    <div class="ruler-track">
      <div class="ruler-fill carteira" style:width={largura(carteira)}></div>
    </div>
    <div class="ruler-val">{fmtPct(carteira)}</div>
  </div>
  {#each indices as indice (indice.chave)}
    <div class="ruler-row">
      <div class="ruler-name">{indiceLabel(indice.chave)}</div>
      <div class="ruler-track">
        <div
          class="ruler-fill"
          style:width={largura(indice.valor)}
          style:background={COR_INDICE[indice.chave] ?? '#8FA3BC'}
        ></div>
      </div>
      <div class="ruler-val">{fmtPct(indice.valor)}</div>
    </div>
  {/each}
</div>
{#if badge}
  <div class="ruler-badge">{badge}</div>
{/if}
