import { api } from './client'

/** KPIs da visão geral. Percentuais em pontos percentuais ("14.2" = 14,2%). */
export interface ResumoCarteira {
  patrimonio: string
  resultado_dia: string
  resultado_dia_pct: string
  rentabilidade_12m: string
  percentual_cdi: string
  quantidade_posicoes: number
  quantidade_classes: number
}

/** Séries acumuladas (base 0% no primeiro mês). `indices` traz apenas os
 * benchmarks solicitados (cdi, ibovespa). */
export interface SerieRentabilidade {
  datas: string[]
  carteira: number[]
  indices: Record<string, number[]>
}

export const obterResumo = () => api.get<ResumoCarteira>('/api/carteira/resumo/')

export const obterRentabilidade = (meses = 12, indices: string[] = ['cdi', 'ibovespa']) =>
  api.get<SerieRentabilidade>(
    `/api/carteira/rentabilidade/?meses=${meses}&indices=${indices.join(',')}`,
  )
