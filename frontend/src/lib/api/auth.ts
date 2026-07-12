/** Autenticação JWT: login, refresh e armazenamento do par de tokens. */

const ACCESS_KEY = 'easyfin.access'
const REFRESH_KEY = 'easyfin.refresh'

export function obterAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY)
}

export function estaAutenticado(): boolean {
  return obterAccessToken() !== null
}

export function limparSessao(): void {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export async function login(username: string, password: string): Promise<boolean> {
  const resp = await fetch('/api/auth/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!resp.ok) return false
  const { access, refresh } = await resp.json()
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
  return true
}

/** Erros de validação por campo devolvidos pelo DRF (ex.: {username: [...]}) */
export type ErrosRegistro = Record<string, string[] | string>

export type ResultadoRegistro = { ok: true } | { ok: false; erros: ErrosRegistro }

export async function registrar(
  username: string,
  email: string,
  password: string,
): Promise<ResultadoRegistro> {
  const resp = await fetch('/api/auth/registro/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  })
  if (resp.status === 201) {
    const { access, refresh } = await resp.json()
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
    return { ok: true }
  }
  const erros = (await resp.json().catch(() => ({}))) as ErrosRegistro
  return { ok: false, erros }
}

export async function renovarToken(): Promise<boolean> {
  const refresh = localStorage.getItem(REFRESH_KEY)
  if (!refresh) return false
  const resp = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
  if (!resp.ok) return false
  const { access } = await resp.json()
  localStorage.setItem(ACCESS_KEY, access)
  return true
}
