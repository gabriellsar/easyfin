<script lang="ts">
  import type { Posicao } from '../api/posicoes'
  import { fmtBRL, fmtPct, fmtPctAbs, fmtQty, classeLabel } from '../utils/format'

  let { posicoes, rotuloTotal = 'Total' }: { posicoes: Posicao[]; rotuloTotal?: string } = $props()

  let subtotal = $derived(
    posicoes.reduce(
      (a, p) => ({
        custo: a.custo + Number(p.custo),
        mercado: a.mercado + Number(p.valor_mercado ?? 0),
        pct: a.pct + Number(p.percentual_carteira ?? 0),
      }),
      { custo: 0, mercado: 0, pct: 0 },
    ),
  )
  let resultadoSub = $derived(subtotal.mercado - subtotal.custo)
</script>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>Ativo</th>
        <th>Classe</th>
        <th>Qtd.</th>
        <th>Preço médio</th>
        <th>Cotação</th>
        <th>Custo</th>
        <th>Valor de mercado</th>
        <th>Resultado (R$)</th>
        <th>Resultado (%)</th>
        <th>% carteira</th>
      </tr>
    </thead>
    <tbody>
      {#each posicoes as p (p.ticker)}
        {@const positivo = Number(p.resultado) >= 0}
        <tr>
          <td>
            <span class="ticker">{p.ticker}</span><br />
            <span class="asset-name">{p.nome}</span>
          </td>
          <td><span class="chip">{classeLabel(p.classe)}</span></td>
          <td class="num">{fmtQty(p.quantidade)}</td>
          <td class="num">{fmtBRL(p.preco_medio)}</td>
          <td class="num">{p.cotacao_atual ? fmtBRL(p.cotacao_atual) : '—'}</td>
          <td class="num">{fmtBRL(p.custo)}</td>
          <td class="num">{p.valor_mercado ? fmtBRL(p.valor_mercado) : '—'}</td>
          <td class="num {positivo ? 'pos' : 'neg'}">
            {(positivo ? '+' : '−') + fmtBRL(Math.abs(Number(p.resultado ?? 0)))}
          </td>
          <td class="num {positivo ? 'pos' : 'neg'}">{fmtPct(p.resultado_pct ?? 0)}</td>
          <td class="num">{fmtPctAbs(p.percentual_carteira ?? 0)}</td>
        </tr>
      {:else}
        <tr>
          <td colspan="10" style="text-align:center;color:var(--muted);padding:26px">
            Nenhuma posição nesta classe. Registre uma compra na aba Operações para começar.
          </td>
        </tr>
      {/each}
    </tbody>
    {#if posicoes.length}
      <tfoot>
        <tr>
          <td>{rotuloTotal}</td>
          <td></td><td></td><td></td><td></td>
          <td>{fmtBRL(subtotal.custo)}</td>
          <td>{fmtBRL(subtotal.mercado)}</td>
          <td class={resultadoSub >= 0 ? 'pos' : 'neg'}>
            {(resultadoSub >= 0 ? '+' : '−') + fmtBRL(Math.abs(resultadoSub))}
          </td>
          <td class={resultadoSub >= 0 ? 'pos' : 'neg'}>
            {fmtPct(subtotal.custo > 0 ? (subtotal.mercado / subtotal.custo - 1) * 100 : 0)}
          </td>
          <td>{fmtPctAbs(subtotal.pct)}</td>
        </tr>
      </tfoot>
    {/if}
  </table>
</div>
