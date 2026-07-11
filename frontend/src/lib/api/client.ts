/** Cliente HTTP base: injeta o JWT, renova o access token em 401 e
 * padroniza o tratamento de erro. As funções por recurso (auth.ts,
 * operacoes.ts, posicoes.ts, carteira.ts) usam apenas este módulo. */

import { obterAccessToken, renovarToken, limparSessao } from './auth'

export class ApiError extends Error {
  constructor(
    public status: number,
    public detalhe: unknown,
  ) {
    super(`API ${status}`)
  }
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const token = obterAccessToken()
  const resp = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  })

  if (resp.status === 401 && retry) {
    const renovado = await renovarToken()
    if (renovado) return request<T>(path, init, false)
    limparSessao()
  }

  if (!resp.ok) {
    throw new ApiError(resp.status, await resp.json().catch(() => null))
  }

  return (await resp.json()) as T
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
}
