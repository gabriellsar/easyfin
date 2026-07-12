<script lang="ts">
  import Overview from './routes/Overview.svelte'
  import Carteira from './routes/Carteira.svelte'
  import Operacoes from './routes/Operacoes.svelte'
  import Login from './routes/Login.svelte'
  import Registro from './routes/Registro.svelte'
  import Landing from './routes/Landing.svelte'
  import Toast from './lib/components/Toast.svelte'
  import { estaAutenticado, limparSessao } from './lib/api/auth'
  import { carteira } from './lib/state/carteira.svelte'
  import { toast } from './lib/state/toast.svelte'
  import { baixarRelatorioExcel } from './lib/api/relatorios'

  const rotas = {
    '/': { pagina: Overview, titulo: 'Visão geral', eyebrow: 'Carteira consolidada' },
    '/carteira': { pagina: Carteira, titulo: 'Carteira', eyebrow: 'Posições e marcação a mercado' },
    '/operacoes': { pagina: Operacoes, titulo: 'Operações', eyebrow: 'Lançamentos e histórico' },
  } as const

  type Rota = keyof typeof rotas | '/login' | '/registro'

  function rotaAtual(): Rota {
    const alvo = location.hash.slice(1) || '/'
    if (alvo === '/login' || alvo === '/registro') return alvo
    return (alvo in rotas ? alvo : '/') as Rota
  }

  let rota = $state<Rota>(rotaAtual())
  let autenticado = $state(estaAutenticado())

  $effect(() => {
    const aoMudarHash = () => (rota = rotaAtual())
    window.addEventListener('hashchange', aoMudarHash)
    return () => window.removeEventListener('hashchange', aoMudarHash)
  })

  $effect(() => {
    if (autenticado) carteira.carregar()
  })

  let rotaApp = $derived(rota === '/login' || rota === '/registro' ? '/' : rota)
  let meta = $derived(rotas[rotaApp])
  let Pagina = $derived(rotas[rotaApp].pagina)

  function entrar() {
    autenticado = true
    location.hash = '#/'
  }

  async function atualizarCotacoes() {
    await carteira.atualizarCotacoes()
    toast.mostrar('Cotações atualizadas — posições remarcadas a mercado')
  }

  async function exportarExcel() {
    try {
      await baixarRelatorioExcel()
      toast.mostrar('Relatório exportado: EasyFin_relatorio.xlsx')
    } catch {
      toast.mostrar('Não foi possível gerar o Excel.')
    }
  }

  function novaOperacao() {
    location.hash = '#/operacoes'
    setTimeout(() => document.getElementById('opQty')?.focus(), 60)
  }

  function sair() {
    limparSessao()
    autenticado = false
    location.hash = '#/'
  }
</script>

{#if !autenticado}
  {#if rota === '/login'}
    <Login aoEntrar={entrar} />
  {:else if rota === '/registro'}
    <Registro aoRegistrar={entrar} />
  {:else}
    <Landing />
  {/if}
{:else}
  <div class="app">
    <aside class="sidebar">
      <div>
        <div class="logo">EasyFin<span class="dot">▪</span></div>
        <div class="logo-sub">Gestão de carteira</div>
      </div>
      <nav aria-label="Navegação principal">
        <a class="nav-btn" class:active={rota === '/'} href="#/">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>
          <span>Visão geral</span>
        </a>
        <a class="nav-btn" class:active={rota === '/carteira'} href="#/carteira">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7h18v13H3z"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/></svg>
          <span>Carteira</span>
        </a>
        <a class="nav-btn" class:active={rota === '/operacoes'} href="#/operacoes">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17l4-8 3 5 3-6"/><path d="M3 3v18h18"/></svg>
          <span>Operações</span>
        </a>
      </nav>
      <div class="sidebar-foot">
        Cotações · <strong>
          {carteira.atualizadoEm?.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
          }) ?? 'últimas conhecidas'}
        </strong><br />
        brapi · Banco Central<br />
        <button class="link-sair" onclick={sair}>Sair</button>
      </div>
    </aside>

    <main class="main">
      <div class="topbar">
        <div>
          <div class="view-eyebrow">{meta.eyebrow}</div>
          <h1 class="view-title">{meta.titulo}</h1>
        </div>
        <div class="actions">
          <button class="btn" onclick={atualizarCotacoes}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-2.6-6.4"/><path d="M21 3v6h-6"/></svg>
            Atualizar cotações
          </button>
          <button class="btn" onclick={exportarExcel}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/></svg>
            Exportar Excel
          </button>
          <button class="btn btn-primary" onclick={novaOperacao}>Nova operação</button>
        </div>
      </div>

      {#if carteira.erro}
        <div class="form-error">{carteira.erro}</div>
      {/if}
      <Pagina />
    </main>
  </div>
{/if}

<Toast />

<style>
  .link-sair {
    background: none;
    border: 0;
    color: #8fa3bc;
    font-family: var(--font-mono);
    font-size: 11px;
    padding: 0;
    text-decoration: underline;
  }
  .link-sair:hover {
    color: #d9e4f0;
  }
</style>
