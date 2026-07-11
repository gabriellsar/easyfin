/** Estado global da carteira (runes do Svelte 5).
 * É apenas CACHE da API — a fonte de verdade é sempre o back-end. */

import { obterResumo, obterRentabilidade } from '../api/carteira'
import type { ResumoCarteira, SerieRentabilidade } from '../api/carteira'
import { listarPosicoes, atualizarCotacoes, type Posicao } from '../api/posicoes'
import {
  listarOperacoes,
  registrarOperacao,
  type Operacao,
  type NovaOperacao,
} from '../api/operacoes'
import { listarAtivos, type Ativo } from '../api/ativos'

class CarteiraState {
  resumo = $state<ResumoCarteira | null>(null)
  posicoes = $state<Posicao[]>([])
  operacoes = $state<Operacao[]>([])
  serie = $state<SerieRentabilidade | null>(null)
  ativos = $state<Ativo[]>([])
  atualizadoEm = $state<Date | null>(null)
  carregando = $state(false)
  erro = $state<string | null>(null)

  async carregar(): Promise<void> {
    this.carregando = true
    this.erro = null
    try {
      const [resumo, posicoes, operacoes, serie, ativos] = await Promise.all([
        obterResumo(),
        listarPosicoes(),
        listarOperacoes(),
        obterRentabilidade(12),
        listarAtivos(),
      ])
      this.resumo = resumo
      this.posicoes = posicoes
      this.operacoes = operacoes.results
      this.serie = serie
      this.ativos = ativos.results
    } catch {
      this.erro = 'Não foi possível carregar os dados da carteira.'
    } finally {
      this.carregando = false
    }
  }

  async registrar(op: NovaOperacao): Promise<void> {
    await registrarOperacao(op)
    await this.carregar()
  }

  async atualizarCotacoes(): Promise<void> {
    await atualizarCotacoes()
    await this.carregar()
    this.atualizadoEm = new Date()
  }
}

export const carteira = new CarteiraState()
