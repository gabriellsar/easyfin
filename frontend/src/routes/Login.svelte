<script lang="ts">
  import { login } from '../lib/api/auth'

  let { aoEntrar }: { aoEntrar: () => void } = $props()

  let username = $state('')
  let password = $state('')
  let erro = $state(false)
  let enviando = $state(false)

  async function submeter(e: SubmitEvent) {
    e.preventDefault()
    enviando = true
    erro = false
    const ok = await login(username, password).catch(() => false)
    enviando = false
    if (ok) aoEntrar()
    else erro = true
  }
</script>

<div class="login-wrap">
  <form class="card login-card" onsubmit={submeter}>
    <div class="logo">EasyFin<span class="dot">▪</span></div>
    <div class="logo-sub">Gestão de carteira</div>

    {#if erro}<div class="form-error">Usuário ou senha inválidos.</div>{/if}

    <div class="field">
      <label for="loginUser">Usuário</label>
      <input id="loginUser" bind:value={username} autocomplete="username" required />
    </div>
    <div class="field">
      <label for="loginPass">Senha</label>
      <input
        id="loginPass"
        type="password"
        bind:value={password}
        autocomplete="current-password"
        required
      />
    </div>
    <button class="btn btn-primary" style="width:100%;justify-content:center" disabled={enviando}>
      {enviando ? 'Entrando…' : 'Entrar'}
    </button>
  </form>
</div>
