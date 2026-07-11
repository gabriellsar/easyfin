class ToastState {
  mensagem = $state('')
  visivel = $state(false)
  #timer: ReturnType<typeof setTimeout> | undefined

  mostrar(mensagem: string): void {
    this.mensagem = mensagem
    this.visivel = true
    clearTimeout(this.#timer)
    this.#timer = setTimeout(() => (this.visivel = false), 2800)
  }
}

export const toast = new ToastState()
