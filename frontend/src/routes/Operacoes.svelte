<script lang="ts">
  import OperationForm from '../lib/components/OperationForm.svelte'
  import { carteira } from '../lib/state/carteira.svelte'
  import { fmtBRL, fmtData, fmtQty } from '../lib/utils/format'
</script>

<div class="op-grid">
  <OperationForm />

  <div class="card">
    <h3>Histórico de operações</h3>
    <div class="sub">{carteira.operacoes.length} operações registradas</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Tipo</th>
            <th>Ativo</th>
            <th>Qtd.</th>
            <th>Preço</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {#each carteira.operacoes as op (op.id)}
            <tr>
              <td class="num">{fmtData(op.data)}</td>
              <td class={op.tipo === 'compra' ? 'side-buy' : 'side-sell'}>
                {op.tipo === 'compra' ? 'Compra' : 'Venda'}
              </td>
              <td><span class="ticker">{op.ticker}</span></td>
              <td class="num">{fmtQty(op.quantidade)}</td>
              <td class="num">{fmtBRL(op.preco_unitario)}</td>
              <td class="num">{fmtBRL(Number(op.preco_unitario) * Number(op.quantidade))}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>
