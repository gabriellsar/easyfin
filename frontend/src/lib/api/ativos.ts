import { api } from './client'
import type { Paginado } from './operacoes'

export interface Ativo {
  id: number
  ticker: string
  nome: string
  classe: string
}

export const listarAtivos = () => api.get<Paginado<Ativo>>('/api/ativos/')
