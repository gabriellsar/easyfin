import { obterAccessToken } from './auth'
import { ApiError } from './client'

export async function baixarRelatorioExcel(): Promise<void> {
  const token = obterAccessToken()
  const resp = await fetch('/api/relatorios/excel/', {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!resp.ok) throw new ApiError(resp.status, null)
  const blob = await resp.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'EasyFin_relatorio.xlsx'
  a.click()
  URL.revokeObjectURL(url)
}
