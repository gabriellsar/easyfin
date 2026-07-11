import { api } from './client'
import type { Paginado } from './operacoes'

export interface Ativo {
  id: number
  ticker: string
  nome: string
  classe: string
  cotacao_atual: string | null
}

export const listarAtivos = () => api.get<Paginado<Ativo>>('/api/ativos/')
