class ToastState {
  mensagem = $state('')
  visivel = $state(false)
  #timer: ReturnType<typeof setTimeout> | undefined

  mostrar(mensagem: string, duracaoMs = 2800): void {
    this.mensagem = mensagem
    this.visivel = true
    clearTimeout(this.#timer)
    this.#timer = setTimeout(() => (this.visivel = false), duracaoMs)
  }
}

export const toast = new ToastState()