<script lang="ts">
  import PositionsTable from '../lib/components/PositionsTable.svelte'
  import { carteira } from '../lib/state/carteira.svelte'
  import { classeLabel } from '../lib/utils/format'

  let filtro = $state('Todas')

  let classes = $derived([
    'Todas',
    ...[...new Set(carteira.posicoes.map((p) => classeLabel(p.classe)))],
  ])
  let posicoesFiltradas = $derived(
    filtro === 'Todas'
      ? carteira.posicoes
      : carteira.posicoes.filter((p) => classeLabel(p.classe) === filtro),
  )
</script>

<div class="filters">
  {#each classes as classe (classe)}
    <button
      class="filter-chip"
      class:active={classe === filtro}
      onclick={() => (filtro = classe)}
    >
      {classe}
    </button>
  {/each}
</div>

<div class="card">
  <PositionsTable
    posicoes={posicoesFiltradas}
    rotuloTotal={filtro === 'Todas' ? 'Total' : `Total — ${filtro}`}
  />
</div>
