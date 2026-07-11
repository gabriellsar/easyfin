import { api } from './client'

export type TipoOperacao = 'compra' | 'venda'

export interface Operacao {
  id: number
  ticker: string
  tipo: TipoOperacao
  quantidade: string
  preco_unitario: string
  data: string
}

export interface NovaOperacao {
  ticker: string
  tipo: TipoOperacao
  quantidade: string
  preco_unitario: string
  data: string
}

export interface Paginado<T> {
  count: number
  results: T[]
}

export const listarOperacoes = () => api.get<Paginado<Operacao>>('/api/operacoes/')

export const registrarOperacao = (op: NovaOperacao) => api.post<Operacao>('/api/operacoes/', op)
