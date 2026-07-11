<script lang="ts">
  import { fmtPct, fmtPctAbs } from '../utils/format'

  let {
    carteira = 0,
    cdi = 0,
    ibovespa = 0,
  }: { carteira?: number; cdi?: number; ibovespa?: number } = $props()

  let linhas = $derived([
    { nome: 'Carteira', valor: carteira, cls: 'carteira' },
    { nome: 'CDI', valor: cdi, cls: 'cdi' },
    { nome: 'Ibovespa', valor: ibovespa, cls: 'ibov' },
  ])
  let maximo = $derived(Math.max(carteira, cdi, ibovespa, 0.001))
  let pctCdi = $derived(cdi !== 0 ? (carteira / cdi) * 100 : 0)
  let difIbov = $derived(carteira - ibovespa)

  let montado = $state(false)
  $effect(() => {
    const raf = requestAnimationFrame(() => (montado = true))
    return () => cancelAnimationFrame(raf)
  })
</script>

<div class="ruler">
  {#each linhas as linha (linha.nome)}
    <div class="ruler-row">
      <div class="ruler-name">{linha.nome}</div>
      <div class="ruler-track">
        <div
          class="ruler-fill {linha.cls}"
          style:width={montado ? `${((linha.valor / maximo) * 100).toFixed(1)}%` : '0'}
        ></div>
      </div>
      <div class="ruler-val">{fmtPct(linha.valor)}</div>
    </div>
  {/each}
</div>
<div class="ruler-badge">
  Carteira entregou {fmtPctAbs(pctCdi, 0)} do CDI e
  {difIbov >= 0
    ? `superou o Ibovespa em ${fmtPctAbs(difIbov)} p.p.`
    : `ficou ${fmtPctAbs(-difIbov)} p.p. abaixo do Ibovespa`}
</div>
