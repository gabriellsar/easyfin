import { api } from './client'

/** Posição consolidada e marcada a mercado — tudo calculado no back.
 * Valores decimais chegam como string (DRF). */
export interface Posicao {
  ticker: string
  nome: string
  classe: string
  quantidade: string
  preco_medio: string
  cotacao_atual: string | null
  custo: string
  valor_mercado: string | null
  resultado: string | null
  resultado_pct: string | null
  percentual_carteira: string | null
}

export const listarPosicoes = () => api.get<Posicao[]>('/api/posicoes/')

export const atualizarCotacoes = () => api.post<void>('/api/cotacoes/atualizar/', {})
