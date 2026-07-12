<script lang="ts">
  import KpiCards from '../lib/components/KpiCards.svelte'
  import BenchmarkRuler from '../lib/components/BenchmarkRuler.svelte'
  import PerformanceChart from '../lib/components/charts/PerformanceChart.svelte'
  import PositionsTable from '../lib/components/PositionsTable.svelte'
  import type { ResumoCarteira, SerieRentabilidade } from '../lib/api/carteira'
  import type { Posicao } from '../lib/api/posicoes'

  // Dados estáticos de demonstração — a landing é pública e não consome a API.
  const demoResumo: ResumoCarteira = {
    patrimonio: '64552.72',
    resultado_dia: '220.12',
    resultado_dia_pct: '0.34',
    rentabilidade_12m: '14.2',
    percentual_cdi: '137.9',
    quantidade_posicoes: 8,
    quantidade_classes: 3,
  }

  const demoSerie: SerieRentabilidade = {
    datas: [
      '2025-07-01', '2025-08-01', '2025-09-01', '2025-10-01', '2025-11-01', '2025-12-01',
      '2026-01-01', '2026-02-01', '2026-03-01', '2026-04-01', '2026-05-01', '2026-06-01',
    ],
    carteira: [0, 1.2, 2.8, 3.5, 5.1, 6.0, 7.4, 8.2, 9.6, 11.3, 12.8, 14.2],
    indices: {
      cdi: [0, 0.9, 1.8, 2.8, 3.7, 4.7, 5.6, 6.5, 7.4, 8.4, 9.3, 10.3],
      ibovespa: [0, 2.1, 1.4, 3.9, 3.2, 5.6, 4.8, 7.5, 8.9, 10.2, 11.6, 12.4],
    },
  }

  const demoPosicoes: Posicao[] = [
    { ticker: 'TSELIC29', nome: 'Tesouro Selic 2029', classe: 'renda_fixa', quantidade: '1', preco_medio: '15102.55', cotacao_atual: '15834.22', custo: '15102.55', valor_mercado: '15834.22', resultado: '731.67', resultado_pct: '4.84', percentual_carteira: '24.53' },
    { ticker: 'PETR4', nome: 'Petrobras PN', classe: 'acao', quantidade: '250', preco_medio: '36.95', cotacao_atual: '41.87', custo: '9237.50', valor_mercado: '10467.50', resultado: '1230.00', resultado_pct: '13.31', percentual_carteira: '16.22' },
    { ticker: 'ITUB4', nome: 'Itaú Unibanco PN', classe: 'acao', quantidade: '250', preco_medio: '34.52', cotacao_atual: '38.12', custo: '8630.00', valor_mercado: '9530.00', resultado: '900.00', resultado_pct: '10.43', percentual_carteira: '14.76' },
    { ticker: 'BBAS3', nome: 'Banco do Brasil ON', classe: 'acao', quantidade: '250', preco_medio: '27.40', cotacao_atual: '29.34', custo: '6850.00', valor_mercado: '7335.00', resultado: '485.00', resultado_pct: '7.08', percentual_carteira: '11.36' },
    { ticker: 'KNRI11', nome: 'Kinea Renda Imob.', classe: 'fii', quantidade: '40', preco_medio: '158.30', cotacao_atual: '165.20', custo: '6332.00', valor_mercado: '6608.00', resultado: '276.00', resultado_pct: '4.36', percentual_carteira: '10.24' },
  ]

  const recursos = [
    {
      titulo: 'Consolidação automática',
      texto: 'Registre compras e vendas e deixe o resto com a gente: preço médio ponderado, validação de saldo e posição consolidada por ativo.',
    },
    {
      titulo: 'Benchmarks de verdade',
      texto: 'Sua rentabilidade lado a lado com o CDI (Banco Central) e o Ibovespa (B3), no mesmo período e na mesma base.',
    },
    {
      titulo: 'Marcação a mercado',
      texto: 'Cotações da B3 atualizadas com um clique e patrimônio remarcado a mercado, com resultado do dia e acumulado.',
    },
    {
      titulo: 'Relatórios em Excel',
      texto: 'Exporte posições e histórico de operações em .xlsx prontos para o seu controle ou para a declaração de IR.',
    },
  ]

  // Planos ilustrativos (mock) — sem cobrança real neste momento.
  const planos = [
    {
      nome: 'Gratuito',
      preco: 'R$ 0',
      periodo: 'para sempre',
      descricao: 'Para começar a organizar a carteira.',
      destaque: false,
      cta: 'Começar grátis',
      itens: [
        '1 carteira',
        'Até 10 ativos',
        'Cotações com atraso de 15 min',
        'Preço médio e consolidação automáticos',
      ],
    },
    {
      nome: 'Investidor',
      preco: 'R$ 19',
      periodo: '/mês',
      descricao: 'Para quem acompanha o mercado de perto.',
      destaque: true,
      cta: 'Assinar Investidor',
      itens: [
        'Carteiras ilimitadas',
        'Cotações em tempo real',
        'Comparação com CDI e Ibovespa',
        'Exportação em Excel',
        'Suporte por e-mail',
      ],
    },
    {
      nome: 'Pro',
      preco: 'R$ 49',
      periodo: '/mês',
      descricao: 'Para gestão profissional e escritórios.',
      destaque: false,
      cta: 'Assinar Pro',
      itens: [
        'Tudo do Investidor',
        'Múltiplos usuários',
        'Relatórios para IR',
        'API de integração',
        'Suporte prioritário',
      ],
    },
  ]

  const anoAtual = new Date().getFullYear()
</script>

<div class="landing">
  <!-- ===== navegação ===== -->
  <header class="lp-nav">
    <div class="wrap lp-nav-inner">
      <div class="logo">EasyFin<span class="dot">▪</span></div>
      <nav aria-label="Navegação da página">
        <a href="#recursos">Recursos</a>
        <a href="#demonstracao">Demonstração</a>
        <a href="#planos">Planos</a>
      </nav>
      <div class="lp-nav-acoes">
        <a class="btn" href="#/login">Entrar</a>
        <a class="btn btn-primary" href="#/registro">Começar grátis</a>
      </div>
    </div>
  </header>

  <!-- ===== hero ===== -->
  <section class="hero">
    <div class="wrap">
      <div class="view-eyebrow">Gestão de carteira de investimentos</div>
      <h1>
        Sua carteira consolidada,<br />
        <span class="destaque-gold">comparada ao que importa.</span>
      </h1>
      <p class="hero-sub">
        Registre operações, acompanhe o preço médio e veja sua rentabilidade lado a lado
        com o CDI e o Ibovespa — com exportação em Excel a um clique.
      </p>
      <div class="hero-ctas">
        <a class="btn btn-primary btn-lg" href="#/registro">Começar grátis</a>
        <a class="btn btn-lg" href="#demonstracao">Ver demonstração</a>
      </div>
      <div class="hero-kpis">
        <KpiCards resumo={demoResumo} periodo="Jul 2025 — Jun 2026" />
      </div>
    </div>
  </section>

  <!-- ===== recursos ===== -->
  <section id="recursos" class="secao">
    <div class="wrap">
      <h2>Tudo o que sua carteira precisa</h2>
      <p class="secao-sub">Do registro da operação ao relatório final, sem planilha manual.</p>
      <div class="recursos-grid">
        {#each recursos as r (r.titulo)}
          <div class="card">
            <h3>{r.titulo}</h3>
            <p class="recurso-texto">{r.texto}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- ===== demonstração com os componentes reais ===== -->
  <section id="demonstracao" class="secao secao-alt">
    <div class="wrap">
      <h2>Veja o EasyFin em ação</h2>
      <p class="secao-sub">
        Componentes reais do produto, com dados de demonstração.
      </p>

      <div class="grid-2">
        <div class="card">
          <h3>Evolução acumulada — 12 meses</h3>
          <div class="sub">Carteira comparada aos benchmarks (base 0% em Jul/25)</div>
          <PerformanceChart serie={demoSerie} />
        </div>
        <div class="card">
          <h3>Carteira vs benchmarks</h3>
          <div class="sub">Rentabilidade acumulada no período</div>
          <BenchmarkRuler
            carteira={14.2}
            indices={[
              { chave: 'cdi', valor: 10.3 },
              { chave: 'ibovespa', valor: 12.4 },
            ]}
          />
        </div>
      </div>

      <div class="card">
        <h3>Posições consolidadas</h3>
        <div class="sub">Preço médio, marcação a mercado e resultado por ativo</div>
        <PositionsTable posicoes={demoPosicoes} rotuloTotal="Total (demonstração)" />
      </div>
    </div>
  </section>

  <!-- ===== planos ===== -->
  <section id="planos" class="secao">
    <div class="wrap">
      <h2>Planos para cada perfil</h2>
      <p class="secao-sub">Comece grátis e evolua quando fizer sentido. Cancele quando quiser.</p>
      <div class="planos-grid">
        {#each planos as plano (plano.nome)}
          <div class="card plano" class:plano-destaque={plano.destaque}>
            {#if plano.destaque}<div class="plano-badge">Mais popular</div>{/if}
            <h3>{plano.nome}</h3>
            <div class="plano-preco">
              <span class="valor">{plano.preco}</span>
              <span class="periodo">{plano.periodo}</span>
            </div>
            <p class="plano-desc">{plano.descricao}</p>
            <ul class="plano-itens">
              {#each plano.itens as item (item)}
                <li>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6 9 17l-5-5" /></svg>
                  {item}
                </li>
              {/each}
            </ul>
            <a class="btn btn-lg plano-cta" class:btn-primary={plano.destaque} href="#/registro">
              {plano.cta}
            </a>
          </div>
        {/each}
      </div>
      <p class="planos-nota">Valores ilustrativos — projeto em desenvolvimento, sem cobrança.</p>
    </div>
  </section>

  <!-- ===== footer ===== -->
  <footer class="lp-footer">
    <div class="wrap">
      <div class="footer-topo">
        <div class="footer-marca">
          <div class="logo">EasyFin<span class="dot">▪</span></div>
          <p>Gestão de carteira de investimentos, do registro da operação ao relatório.</p>
          <div class="footer-social">
            <a href="https://github.com" target="_blank" rel="noreferrer" aria-label="GitHub">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.55v-2.15c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.19 1.76 1.19 1.03 1.76 2.7 1.25 3.35.95.1-.74.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11.1 11.1 0 0 1 5.78 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.69 5.38-5.26 5.66.41.36.78 1.06.78 2.14v3.17c0 .3.21.67.8.55A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z"/></svg>
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noreferrer" aria-label="LinkedIn">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.56V9h3.56v11.45Z"/></svg>
            </a>
            <a href="https://x.com" target="_blank" rel="noreferrer" aria-label="X">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.66l-5.21-6.82-5.97 6.82H1.67l7.73-8.84L1.25 2.25h6.83l4.71 6.23 5.45-6.23Zm-1.16 17.52h1.83L7.08 4.13H5.12l11.96 15.64Z"/></svg>
            </a>
          </div>
        </div>
        <div class="footer-colunas">
          <div>
            <h4>Produto</h4>
            <a href="#recursos">Recursos</a>
            <a href="#demonstracao">Demonstração</a>
            <a href="#planos">Planos</a>
          </div>
          <div>
            <h4>Empresa</h4>
            <a href="#recursos">Sobre</a>
            <a href="#recursos">Blog</a>
            <a href="#recursos">Contato</a>
          </div>
          <div>
            <h4>Legal</h4>
            <a href="#recursos">Termos de uso</a>
            <a href="#recursos">Privacidade</a>
            <a href="#recursos">Cookies</a>
          </div>
        </div>
      </div>
      <div class="footer-base">
        <span>© {anoAtual} EasyFin. Todos os direitos reservados.</span>
        <span class="footer-disclaimer">
          O EasyFin é uma ferramenta de organização de carteira. As informações exibidas
          não constituem recomendação de investimento. Rentabilidade passada não garante
          resultados futuros.
        </span>
      </div>
    </div>
  </footer>
</div>

<style>
  .landing {
    background: var(--paper);
    min-height: 100vh;
  }
  .wrap {
    max-width: 1180px;
    margin: 0 auto;
    padding: 0 30px;
  }

  /* navegação */
  .lp-nav {
    position: sticky;
    top: 0;
    z-index: 20;
    background: rgba(244, 246, 249, 0.92);
    backdrop-filter: blur(6px);
    border-bottom: 1px solid var(--line);
  }
  .lp-nav-inner {
    display: flex;
    align-items: center;
    gap: 26px;
    padding-top: 14px;
    padding-bottom: 14px;
  }
  .lp-nav .logo {
    color: var(--ink);
  }
  .lp-nav nav {
    display: flex;
    gap: 20px;
    flex: 1;
  }
  .lp-nav nav a {
    color: var(--muted);
    text-decoration: none;
    font-size: 13.5px;
    font-weight: 500;
  }
  .lp-nav nav a:hover {
    color: var(--ink);
  }
  .lp-nav-acoes {
    display: flex;
    gap: 10px;
  }
  .lp-nav-acoes .btn {
    text-decoration: none;
  }

  /* hero */
  .hero {
    padding: 72px 0 56px;
    text-align: center;
  }
  .hero h1 {
    font-family: var(--font-display);
    font-size: 44px;
    line-height: 1.15;
    font-weight: 700;
    color: var(--ink);
    margin: 14px 0 16px;
    letter-spacing: -0.5px;
  }
  .destaque-gold {
    color: var(--gold);
  }
  .hero-sub {
    max-width: 560px;
    margin: 0 auto 26px;
    color: var(--muted);
    font-size: 15.5px;
  }
  .hero-ctas {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 44px;
  }
  .btn-lg {
    padding: 12px 22px;
    font-size: 14px;
    text-decoration: none;
  }
  .hero-kpis {
    text-align: left;
  }

  /* seções */
  .secao {
    padding: 56px 0;
    scroll-margin-top: 64px;
  }
  .secao-alt {
    background: #fff;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
  }
  .secao-alt :global(.card) {
    background: var(--paper);
  }
  .secao h2 {
    font-family: var(--font-display);
    font-size: 28px;
    font-weight: 600;
    color: var(--ink);
    text-align: center;
    margin-bottom: 6px;
  }
  .secao-sub {
    text-align: center;
    color: var(--muted);
    margin-bottom: 30px;
  }
  .secao :global(.grid-2) {
    text-align: left;
  }

  /* recursos */
  .recursos-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
  }
  .recurso-texto {
    font-size: 13px;
    color: var(--muted);
    margin-top: 8px;
  }

  /* planos */
  .planos-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    align-items: stretch;
  }
  .plano {
    display: flex;
    flex-direction: column;
    position: relative;
    padding: 24px;
  }
  .plano-destaque {
    border-color: var(--gold);
    box-shadow: 0 8px 24px rgba(185, 138, 47, 0.12);
  }
  .plano-badge {
    position: absolute;
    top: -11px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--gold);
    color: #fff;
    font-family: var(--font-mono);
    font-size: 10.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 12px;
    border-radius: 99px;
    white-space: nowrap;
  }
  .plano-preco {
    margin: 10px 0 4px;
  }
  .plano-preco .valor {
    font-family: var(--font-mono);
    font-size: 32px;
    font-weight: 600;
    color: var(--ink);
  }
  .plano-preco .periodo {
    color: var(--muted);
    font-size: 13px;
  }
  .plano-desc {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 16px;
  }
  .plano-itens {
    list-style: none;
    padding: 0;
    margin: 0 0 22px;
    display: grid;
    gap: 9px;
    flex: 1;
  }
  .plano-itens li {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 13px;
  }
  .plano-itens svg {
    color: var(--up);
    flex: none;
  }
  .plano-cta {
    justify-content: center;
  }
  .planos-nota {
    text-align: center;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 11.5px;
    margin-top: 22px;
  }

  /* footer */
  .lp-footer {
    background: var(--ink);
    color: #b9c7d9;
    padding: 48px 0 28px;
    font-size: 13px;
  }
  .footer-topo {
    display: grid;
    grid-template-columns: 1.4fr 2fr;
    gap: 40px;
    padding-bottom: 32px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  }
  .footer-marca p {
    margin: 10px 0 16px;
    max-width: 280px;
    color: #8fa3bc;
  }
  .footer-social {
    display: flex;
    gap: 14px;
  }
  .footer-social a {
    color: #8fa3bc;
  }
  .footer-social a:hover {
    color: #fff;
  }
  .footer-colunas {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
  .footer-colunas h4 {
    font-family: var(--font-mono);
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #d9e4f0;
    margin-bottom: 12px;
  }
  .footer-colunas a {
    display: block;
    color: #8fa3bc;
    text-decoration: none;
    margin-bottom: 9px;
  }
  .footer-colunas a:hover {
    color: #fff;
  }
  .footer-base {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-top: 22px;
  }
  .footer-disclaimer {
    color: #8fa3bc;
    font-size: 11.5px;
    max-width: 720px;
  }

  /* responsivo */
  @media (max-width: 980px) {
    .lp-nav nav {
      display: none;
    }
    .lp-nav-inner {
      justify-content: space-between;
    }
    .hero h1 {
      font-size: 32px;
    }
    .recursos-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    .planos-grid {
      grid-template-columns: 1fr;
    }
    .footer-topo {
      grid-template-columns: 1fr;
      gap: 28px;
    }
  }
  @media (max-width: 560px) {
    .recursos-grid {
      grid-template-columns: 1fr;
    }
    .hero-ctas {
      flex-direction: column;
      align-items: center;
    }
  }
</style>
