<script lang="ts">
  /** Formulário de compra/venda. Validação aqui é só UX — o back revalida
   * saldo e recalcula o preço médio. */

  import type { TipoOperacao } from '../api/operacoes'
  import { ApiError } from '../api/client'
  import { carteira } from '../state/carteira.svelte'
  import { toast } from '../state/toast.svelte'
  import { fmtBRL, fmtQty } from '../utils/format'

  let tipo = $state<TipoOperacao>('compra')
  let ticker = $state('')
  let quantidade = $state('')
  let preco = $state('')
  let data = $state(new Date().toISOString().slice(0, 10))
  let erro = $state<string | null>(null)
  let enviando = $state(false)

  let posicaoAtual = $derived(carteira.posicoes.find((p) => p.ticker === ticker))

  function prefillPreco() {
    const cot = carteira.ativos.find((a) => a.ticker === ticker)?.cotacao_atual
    if (cot) preco = Number(cot).toFixed(2)
  }

  $effect(() => {
    if (!ticker && carteira.ativos.length) {
      ticker = carteira.ativos[0].ticker
      prefillPreco()
    }
  })

  async function submeter() {
    erro = null
    const qtd = Number(quantidade)
    const precoNum = Number(preco)
    if (!qtd || qtd <= 0) return void (erro = 'Informe uma quantidade maior que zero.')
    if (!precoNum || precoNum <= 0)
      return void (erro = 'Informe um preço unitário maior que zero.')
    if (!data) return void (erro = 'Informe a data da operação.')
    if (tipo === 'venda') {
      const disponivel = Number(posicaoAtual?.quantidade ?? 0)
      if (qtd > disponivel) {
        erro = `Quantidade indisponível: você possui ${fmtQty(disponivel)} un. de ${ticker}.`
        return
      }
    }

    enviando = true
    try {
      await carteira.registrar({
        ticker,
        tipo,
        quantidade: String(qtd),
        preco_unitario: String(precoNum),
        data,
      })
      quantidade = ''
      toast.mostrar(`${tipo === 'compra' ? 'Compra' : 'Venda'} de ${fmtQty(qtd)} ${ticker} registrada`)
    } catch (e) {
      erro =
        e instanceof ApiError && e.status === 400
          ? 'Operação recusada pelo servidor (verifique o saldo disponível).'
          : 'Erro ao registrar a operação.'
    } finally {
      enviando = false
    }
  }
</script>

<div class="card">
  <h3>Registrar operação</h3>
  <div class="sub">Compras recalculam o preço médio; vendas reduzem a posição</div>

  {#if erro}<div class="form-error">{erro}</div>{/if}

  <div class="field">
    <label id="lblTipo" for="segBuy">Tipo</label>
    <div class="seg" role="group" aria-labelledby="lblTipo">
      <button
        id="segBuy"
        type="button"
        class="buy"
        class:active={tipo === 'compra'}
        onclick={() => (tipo = 'compra')}>Compra</button
      >
      <button
        type="button"
        class="sell"
        class:active={tipo === 'venda'}
        onclick={() => (tipo = 'venda')}>Venda</button
      >
    </div>
  </div>

  <div class="field">
    <label for="opAsset">Ativo</label>
    <select id="opAsset" bind:value={ticker} onchange={prefillPreco}>
      {#each carteira.ativos as a (a.ticker)}
        <option value={a.ticker}>{a.ticker} — {a.nome}</option>
      {/each}
    </select>
  </div>
  <div class="form-hint">
    {posicaoAtual
      ? `Posição atual: ${fmtQty(posicaoAtual.quantidade)} un. · PM ${fmtBRL(posicaoAtual.preco_medio)}`
      : 'Sem posição neste ativo'}
  </div>

  <div class="row-2">
    <div class="field">
      <label for="opQty">Quantidade</label>
      <input id="opQty" type="number" min="1" step="1" placeholder="0" bind:value={quantidade} />
    </div>
    <div class="field">
      <label for="opPrice">Preço unitário (R$)</label>
      <input id="opPrice" type="number" min="0.01" step="0.01" placeholder="0,00" bind:value={preco} />
    </div>
  </div>

  <div class="field">
    <label for="opDate">Data</label>
    <input id="opDate" type="date" bind:value={data} />
  </div>

  <button
    class="btn btn-primary"
    style="width:100%;justify-content:center"
    disabled={enviando}
    onclick={submeter}
  >
    {enviando ? 'Registrando…' : tipo === 'compra' ? 'Registrar compra' : 'Registrar venda'}
  </button>
</div>
