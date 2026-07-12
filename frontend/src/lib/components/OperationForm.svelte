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

  let tickerNormalizado = $derived(ticker.trim().toUpperCase())
  let posicaoAtual = $derived(carteira.posicoes.find((p) => p.ticker === tickerNormalizado))
  let ativoConhecido = $derived(carteira.ativos.find((a) => a.ticker === tickerNormalizado))

  async function submeter() {
    erro = null
    const qtd = Number(quantidade)
    const precoNum = Number(preco)
    if (!tickerNormalizado) return void (erro = 'Informe o ticker do ativo.')
    if (!qtd || qtd <= 0) return void (erro = 'Informe uma quantidade maior que zero.')
    if (!precoNum || precoNum <= 0)
      return void (erro = 'Informe um preço unitário maior que zero.')
    if (!data) return void (erro = 'Informe a data da operação.')
    if (tipo === 'venda') {
      const disponivel = Number(posicaoAtual?.quantidade ?? 0)
      if (qtd > disponivel) {
        erro = `Quantidade indisponível: você possui ${fmtQty(disponivel)} un. de ${tickerNormalizado}.`
        return
      }
    }

    enviando = true
    try {
      await carteira.registrar({
        ticker: tickerNormalizado,
        tipo,
        quantidade: String(qtd),
        preco_unitario: String(precoNum),
        data,
      })
      quantidade = ''
      toast.mostrar(
        `${tipo === 'compra' ? 'Compra' : 'Venda'} de ${fmtQty(qtd)} ${tickerNormalizado} registrada`,
      )
    } catch (e) {
      // o back devolve a causa exata (ticker inexistente na B3, saldo, etc.)
      const detalhe =
        e instanceof ApiError && typeof (e.detalhe as any)?.detail === 'string'
          ? (e.detalhe as any).detail
          : null
      erro = detalhe ?? 'Erro ao registrar a operação.'
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
    <input
      id="opAsset"
      list="opAtivosSugestoes"
      placeholder="ex.: PETR4, BBDC4, HGLG11"
      bind:value={ticker}
      autocomplete="off"
      spellcheck="false"
      style="text-transform: uppercase"
    />
  </div>
  <div class="form-hint">
    {#if posicaoAtual}
      Posição atual: {fmtQty(posicaoAtual.quantidade)} un. · PM {fmtBRL(posicaoAtual.preco_medio)}
    {:else if tickerNormalizado && !ativoConhecido}
      Ativo novo — será buscado na B3 ao registrar
    {:else}
      Sem posição neste ativo
    {/if}
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
