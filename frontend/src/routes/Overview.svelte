<script lang="ts">
  import KpiCards from '../lib/components/KpiCards.svelte'
  import BenchmarkRuler from '../lib/components/BenchmarkRuler.svelte'
  import PerformanceChart from '../lib/components/charts/PerformanceChart.svelte'
  import AllocationDonut from '../lib/components/charts/AllocationDonut.svelte'
  import { carteira } from '../lib/state/carteira.svelte'
  import { fmtBRL, fmtPct, fmtQty } from '../lib/utils/format'

  let top5 = $derived(
    [...carteira.posicoes]
      .sort((a, b) => Number(b.valor_mercado ?? 0) - Number(a.valor_mercado ?? 0))
      .slice(0, 5),
  )
</script>

<KpiCards resumo={carteira.resumo} />

<div class="grid-2">
  <div class="card">
    <h3>Evolução acumulada — 12 meses</h3>
    <div class="sub">Carteira comparada aos benchmarks (base 0% no primeiro mês)</div>
    <PerformanceChart serie={carteira.serie} />
  </div>
  <div class="card">
    <h3>Carteira vs benchmarks</h3>
    <div class="sub">Rentabilidade acumulada no período</div>
    <BenchmarkRuler
      carteira={carteira.serie?.carteira.at(-1) ?? 0}
      cdi={carteira.serie?.cdi.at(-1) ?? 0}
      ibovespa={carteira.serie?.ibovespa.at(-1) ?? 0}
    />
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
