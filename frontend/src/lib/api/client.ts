/** Cliente HTTP base: injeta o JWT, renova o access token em 401 e
 * padroniza o tratamento de erro. As funções por recurso (auth.ts,
 * operacoes.ts, posicoes.ts, carteira.ts) usam apenas este módulo. */

import { obterAccessToken, renovarToken, limparSessao } from './auth'
import { toast } from '../state/toast.svelte'

/** Após quanto tempo sem resposta avisamos que o Render está acordando. */
const LIMIAR_AVISO_HIBERNACAO_MS = 3000
const AVISO_HIBERNACAO =
  'Aviso: O backend está hospedado em um ambiente gratuito e está despertando da hibernação. Isso leva cerca de 40 segundos.'

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
  const avisoTimer = setTimeout(
    () => toast.mostrar(AVISO_HIBERNACAO, 10000),
    LIMIAR_AVISO_HIBERNACAO_MS,
  )
  try {
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
  } finally {
    clearTimeout(avisoTimer)
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
}
