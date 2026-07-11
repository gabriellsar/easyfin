/** Formatação pt-BR (portada do protótipo) — formatar é papel do front;
 * calcular, do back. Percentuais chegam em pontos percentuais (14.2 = 14,2%). */

export const fmtBRL = (v: number | string) =>
  Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export const fmtPct = (v: number | string, d = 1) => {
  const n = Number(v)
  return (
    (n >= 0 ? '+' : '') +
    n.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d }) +
    '%'
  )
}

export const fmtPctAbs = (v: number | string, d = 1) =>
  Number(v).toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d }) + '%'

export const fmtQty = (v: number | string) => Number(v).toLocaleString('pt-BR')

export const fmtData = (iso: string) => {
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y}`
}

/** "2025-07-01" -> "Jul/25" (rótulos dos gráficos) */
export const fmtMesAno = (iso: string) => {
  const d = new Date(`${iso}T00:00:00`)
  const mes = d.toLocaleDateString('pt-BR', { month: 'short' }).replace('.', '')
  return mes.charAt(0).toUpperCase() + mes.slice(1) + '/' + String(d.getFullYear()).slice(2)
}

/** "2025-07-01" -> "Jul 2025" (período dos KPIs) */
export const fmtMesAnoLongo = (iso: string) => {
  const d = new Date(`${iso}T00:00:00`)
  const mes = d.toLocaleDateString('pt-BR', { month: 'short' }).replace('.', '')
  return mes.charAt(0).toUpperCase() + mes.slice(1) + ' ' + d.getFullYear()
}

/** Rótulos de exibição das classes de ativo (a API usa slugs). */
export const CLASSE_LABEL: Record<string, string> = {
  acao: 'Ações',
  fii: 'FIIs',
  renda_fixa: 'Renda Fixa',
  etf: 'ETFs',
}

export const classeLabel = (slug: string) => CLASSE_LABEL[slug] ?? slug
