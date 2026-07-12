<script lang="ts">
  import KpiCards from '../lib/components/KpiCards.svelte'
  import BenchmarkRuler from '../lib/components/BenchmarkRuler.svelte'
  import PerformanceChart from '../lib/components/charts/PerformanceChart.svelte'
  import AllocationDonut from '../lib/components/charts/AllocationDonut.svelte'
  import { carteira } from '../lib/state/carteira.svelte'
  import {
    fmtBRL,
    fmtPct,
    fmtQty,
    fmtMesAno,
    fmtMesAnoLongo,
    INDICES_DISPONIVEIS,
    indiceLabel,
  } from '../lib/utils/format'

  let top5 = $derived(
    [...carteira.posicoes]
      .sort((a, b) => Number(b.valor_mercado ?? 0) - Number(a.valor_mercado ?? 0))
      .slice(0, 5),
  )
  let datas = $derived(carteira.serie?.datas ?? [])
  let periodo = $derived(
    datas.length ? `${fmtMesAnoLongo(datas[0])} — ${fmtMesAnoLongo(datas.at(-1)!)}` : null,
  )
  let indicesRuler = $derived(
    Object.entries(carteira.serie?.indices ?? {}).map(([chave, valores]) => ({
      chave,
      valor: valores.at(-1) ?? 0,
    })),
  )
</script>

<KpiCards resumo={carteira.resumo} {periodo} />

<div class="grid-2">
  <div class="card">
    <div class="chart-topo">
      <div>
        <h3>Evolução acumulada — 12 meses</h3>
        <div class="sub">
          Carteira comparada aos benchmarks
          {datas.length ? `(base 0% em ${fmtMesAno(datas[0])})` : ''}
        </div>
      </div>
      <div class="filters indices" role="group" aria-label="Benchmarks exibidos">
        {#each INDICES_DISPONIVEIS as chave (chave)}
          <button
            class="filter-chip"
            class:active={carteira.indicesSelecionados.includes(chave)}
            onclick={() => carteira.alternarIndice(chave)}
          >
            {indiceLabel(chave)}
          </button>
        {/each}
      </div>
    </div>
    <PerformanceChart serie={carteira.serie} />
  </div>
  <div class="card">
    <h3>Carteira vs benchmarks</h3>
    <div class="sub">Rentabilidade acumulada no período</div>
    <BenchmarkRuler carteira={carteira.serie?.carteira.at(-1) ?? 0} indices={indicesRuler} />
  </div>
</div>

<div class="grid-2">
  <div class="card">
    <h3>Maiores posições</h3>
    <div class="sub">Cinco maiores por valor de mercado</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Ativo</th>
            <th>Qtd.</th>
            <th>Preço médio</th>
            <th>Cotação</th>
            <th>Valor de mercado</th>
            <th>Resultado</th>
          </tr>
        </thead>
        <tbody>
          {#each top5 as p (p.ticker)}
            <tr>
              <td>
                <span class="ticker">{p.ticker}</span><br />
                <span class="asset-name">{p.nome}</span>
              </td>
              <td class="num">{fmtQty(p.quantidade)}</td>
              <td class="num">{fmtBRL(p.preco_medio)}</td>
              <td class="num">{p.cotacao_atual ? fmtBRL(p.cotacao_atual) : '—'}</td>
              <td class="num">{p.valor_mercado ? fmtBRL(p.valor_mercado) : '—'}</td>
              <td class="num {Number(p.resultado) >= 0 ? 'pos' : 'neg'}">
                {fmtPct(p.resultado_pct ?? 0)}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
  <div class="card">
    <h3>Alocação por classe</h3>
    <div class="sub">Percentual do patrimônio a mercado</div>
    <AllocationDonut posicoes={carteira.posicoes} />
  </div>
</div>

<style>
  .chart-topo {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
  }
  .indices {
    margin-bottom: 0;
  }
</style>
