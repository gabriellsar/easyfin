<script lang="ts">
  /** Criação de conta. Validação aqui é só UX — o back valida unicidade do
   * usuário e a força da senha (validadores do Django). */

  import { registrar } from '../lib/api/auth'

  let { aoRegistrar }: { aoRegistrar: () => void } = $props()

  let username = $state('')
  let email = $state('')
  let password = $state('')
  let confirmacao = $state('')
  let erro = $state<string | null>(null)
  let enviando = $state(false)

  function primeiroErro(erros: Record<string, string[] | string>): string {
    for (const campo of ['username', 'password', 'email', 'detail']) {
      const v = erros[campo]
      if (v) return Array.isArray(v) ? v[0] : v
    }
    return 'Não foi possível criar a conta. Tente novamente.'
  }

  async function submeter(e: SubmitEvent) {
    e.preventDefault()
    erro = null
    if (password !== confirmacao) {
      erro = 'As senhas não coincidem.'
      return
    }
    enviando = true
    try {
      const resultado = await registrar(username.trim(), email.trim(), password)
      if (resultado.ok) aoRegistrar()
      else erro = primeiroErro(resultado.erros)
    } catch {
      erro = 'Não foi possível criar a conta. Tente novamente.'
    } finally {
      enviando = false
    }
  }
</script>

<div class="login-wrap">
  <form class="card login-card" onsubmit={submeter}>
    <div class="logo">EasyFin<span class="dot">▪</span></div>
    <div class="logo-sub">Criar conta gratuita</div>

    {#if erro}<div class="form-error">{erro}</div>{/if}

    <div class="field">
      <label for="regUser">Usuário</label>
      <input id="regUser" bind:value={username} autocomplete="username" required />
    </div>
    <div class="field">
      <label for="regEmail">E-mail <span class="opcional">(opcional)</span></label>
      <input id="regEmail" type="email" bind:value={email} autocomplete="email" />
    </div>
    <div class="field">
      <label for="regPass">Senha</label>
      <input
        id="regPass"
        type="password"
        bind:value={password}
        autocomplete="new-password"
        minlength="8"
        required
      />
    </div>
    <div class="field">
      <label for="regPass2">Confirmar senha</label>
      <input
        id="regPass2"
        type="password"
        bind:value={confirmacao}
        autocomplete="new-password"
        required
      />
    </div>

    <button class="btn btn-primary" style="width:100%;justify-content:center" disabled={enviando}>
      {enviando ? 'Criando conta…' : 'Criar conta'}
    </button>

    <p class="alternativa">Já tem conta? <a href="#/login">Entrar</a></p>
    <a class="voltar" href="#/">← Voltar ao site</a>
  </form>
</div>

<style>
  .opcional {
    color: var(--muted);
    font-weight: 400;
  }
  .alternativa {
    text-align: center;
    margin-top: 14px;
    font-size: 13px;
    color: var(--muted);
  }
  .alternativa a {
    color: var(--ink-2);
    font-weight: 600;
    text-decoration: none;
  }
  .voltar {
    display: block;
    text-align: center;
    margin-top: 8px;
    font-size: 12.5px;
    color: var(--muted);
    text-decoration: none;
  }
  .voltar:hover {
    color: var(--ink);
  }
</style>
