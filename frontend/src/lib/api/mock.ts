/** Fixtures de desenvolvimento — imitam as respostas da API enquanto os
 * endpoints de dados retornam 501. Os dados e o cálculo espelham o protótipo
 * (easyfin-ui.html) apenas para a UI funcionar; a fonte de verdade continua
 * sendo o back-end. APAGAR este módulo quando os passos 1–5 estiverem prontos. */

import type { Ativo } from './ativos'
import type { Operacao, NovaOperacao } from './operacoes'
import type { Posicao } from './posicoes'
import type { ResumoCarteira, SerieRentabilidade } from './carteira'

const ATIVOS: Ativo[] = [
  { id: 1, ticker: 'PETR4', nome: 'Petrobras PN', classe: 'acao' },
  { id: 2, ticker: 'VALE3', nome: 'Vale ON', classe: 'acao' },
  { id: 3, ticker: 'ITUB4', nome: 'Itaú Unibanco PN', classe: 'acao' },
  { id: 4, ticker: 'WEGE3', nome: 'WEG ON', classe: 'acao' },
  { id: 5, ticker: 'BBAS3', nome: 'Banco do Brasil ON', classe: 'acao' },
  { id: 6, ticker: 'KNRI11', nome: 'Kinea Renda Imob.', classe: 'fii' },
  { id: 7, ticker: 'MXRF11', nome: 'Maxi Renda', classe: 'fii' },
  { id: 8, ticker: 'TSELIC29', nome: 'Tesouro Selic 2029', classe: 'renda_fixa' },
]

const cotacoes: Record<string, number> = {
  PETR4: 41.87,
  VALE3: 63.4,
  ITUB4: 38.12,
  WEGE3: 42.75,
  BBAS3: 29.34,
  KNRI11: 165.2,
  MXRF11: 10.42,
  TSELIC29: 15834.22,
}

const fechamentoAnterior: Record<string, number> = {
  PETR4: 41.52,
  VALE3: 63.95,
  ITUB4: 37.88,
  WEGE3: 42.6,
  BBAS3: 29.1,
  KNRI11: 164.8,
  MXRF11: 10.4,
  TSELIC29: 15827.1,
}

let proximoId = 13
const operacoes: Operacao[] = (
  [
    ['2025-08-05', 'compra', 'PETR4', 200, 36.1],
    ['2025-08-05', 'compra', 'ITUB4', 150, 33.4],
    ['2025-09-12', 'compra', 'VALE3', 100, 59.8],
    ['2025-10-03', 'compra', 'WEGE3', 120, 38.95],
    ['2025-10-20', 'compra', 'KNRI11', 40, 158.3],
    ['2025-11-14', 'compra', 'MXRF11', 500, 10.15],
    ['2025-12-02', 'compra', 'TSELIC29', 1, 15102.55],
    ['2026-01-15', 'compra', 'PETR4', 100, 38.65],
    ['2026-02-20', 'venda', 'VALE3', 30, 65.1],
    ['2026-03-18', 'compra', 'BBAS3', 250, 27.4],
    ['2026-05-06', 'compra', 'ITUB4', 100, 36.2],
    ['2026-06-24', 'venda', 'PETR4', 50, 42.3],
  ] as const
).map(([data, tipo, ticker, qtd, preco], i) => ({
  id: i + 1,
  ticker,
  tipo,
  quantidade: String(qtd),
  preco_unitario: preco.toFixed(2),
  data,
}))

const serie: SerieRentabilidade = {
  datas: [
    '2025-07-01', '2025-08-01', '2025-09-01', '2025-10-01', '2025-11-01', '2025-12-01',
    '2026-01-01', '2026-02-01', '2026-03-01', '2026-04-01', '2026-05-01', '2026-06-01',
  ],
  carteira: [0, 1.2, 2.8, 3.5, 5.1, 6.0, 7.4, 8.2, 9.6, 11.3, 12.8, 14.2],
  cdi: [0, 0.9, 1.8, 2.8, 3.7, 4.7, 5.6, 6.5, 7.4, 8.4, 9.3, 10.3],
  ibovespa: [0, 2.1, 1.4, 3.9, 3.2, 5.6, 4.8, 7.5, 8.9, 10.2, 11.6, 12.4],
}

/** Espelho do computePositions do protótipo (só para as fixtures). */
function calcularPosicoes(): Posicao[] {
  const mapa: Record<string, { qtd: number; pm: number }> = {}
  const ops = [...operacoes].sort((a, b) => a.data.localeCompare(b.data))
  for (const op of ops) {
    const p = (mapa[op.ticker] ??= { qtd: 0, pm: 0 })
    const qtd = Number(op.quantidade)
    const preco = Number(op.preco_unitario)
    if (op.tipo === 'compra') {
      p.pm = p.qtd + qtd > 0 ? (p.pm * p.qtd + preco * qtd) / (p.qtd + qtd) : preco
      p.qtd += qtd
    } else {
      p.qtd -= qtd // venda mantém o preço médio
    }
  }
  const brutas = Object.entries(mapa)
    .filter(([, p]) => p.qtd > 0)
    .map(([ticker, p]) => {
      const ativo = ATIVOS.find((a) => a.ticker === ticker)!
      const cot = cotacoes[ticker]
      const custo = p.pm * p.qtd
      const mercado = cot * p.qtd
      return { ativo, ...p, cot, custo, mercado }
    })
    .sort((a, b) => b.mercado - a.mercado)

  const total = brutas.reduce((s, p) => s + p.mercado, 0)
  return brutas.map((p) => ({
    ticker: p.ativo.ticker,
    nome: p.ativo.nome,
    classe: p.ativo.classe,
    quantidade: String(p.qtd),
    preco_medio: p.pm.toFixed(2),
    cotacao_atual: p.cot.toFixed(2),
    custo: p.custo.toFixed(2),
    valor_mercado: p.mercado.toFixed(2),
    resultado: (p.mercado - p.custo).toFixed(2),
    resultado_pct: p.custo > 0 ? ((p.mercado / p.custo - 1) * 100).toFixed(2) : '0',
    percentual_carteira: total > 0 ? ((p.mercado / total) * 100).toFixed(2) : '0',
  }))
}

function calcularResumo(posicoes: Posicao[]): ResumoCarteira {
  const total = posicoes.reduce((s, p) => s + Number(p.valor_mercado), 0)
  const dia = posicoes.reduce(
    (s, p) =>
      s + (Number(p.cotacao_atual) - fechamentoAnterior[p.ticker]) * Number(p.quantidade),
    0,
  )
  const r12 = serie.carteira.at(-1)!
  const cdi12 = serie.cdi.at(-1)!
  return {
    patrimonio: total.toFixed(2),
    resultado_dia: dia.toFixed(2),
    resultado_dia_pct: (total - dia > 0 ? (dia / (total - dia)) * 100 : 0).toFixed(2),
    rentabilidade_12m: r12.toFixed(1),
    percentual_cdi: ((r12 / cdi12) * 100).toFixed(0),
    quantidade_posicoes: posicoes.length,
    quantidade_classes: new Set(posicoes.map((p) => p.classe)).size,
  }
}

export interface SnapshotMock {
  ativos: Ativo[]
  operacoes: Operacao[]
  posicoes: Posicao[]
  resumo: ResumoCarteira
  serie: SerieRentabilidade
}

export function snapshotMock(): SnapshotMock {
  const posicoes = calcularPosicoes()
  return {
    ativos: ATIVOS,
    operacoes: [...operacoes].sort((a, b) => b.data.localeCompare(a.data)),
    posicoes,
    resumo: calcularResumo(posicoes),
    serie,
  }
}

export function registrarOperacaoMock(op: NovaOperacao): void {
  operacoes.push({
    id: proximoId++,
    ticker: op.ticker,
    tipo: op.tipo,
    quantidade: op.quantidade,
    preco_unitario: op.preco_unitario,
    data: op.data,
  })
}

export function atualizarCotacoesMock(): void {
  for (const t of Object.keys(cotacoes)) {
    const drift = t === 'TSELIC29' ? 0.0004 : (Math.random() - 0.48) * 0.012
    cotacoes[t] = +(cotacoes[t] * (1 + drift)).toFixed(2)
  }
}

export function cotacaoMock(ticker: string): number | undefined {
  return cotacoes[ticker]
}
