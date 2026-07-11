/** Estado global da carteira (runes do Svelte 5).
 * É apenas CACHE da API — a fonte de verdade é sempre o back-end.
 * Enquanto os endpoints de dados retornam 501, cai nas fixtures simuladas
 * (lib/api/mock.ts), como o protótipo fazia. */

import { obterResumo, obterRentabilidade } from '../api/carteira'
import type { ResumoCarteira, SerieRentabilidade } from '../api/carteira'
import { listarPosicoes, atualizarCotacoes, type Posicao } from '../api/posicoes'
import { listarOperacoes, registrarOperacao, type Operacao, type NovaOperacao } from '../api/operacoes'
import { listarAtivos, type Ativo } from '../api/ativos'
import {
  snapshotMock,
  registrarOperacaoMock,
  atualizarCotacoesMock,
} from '../api/mock'

class CarteiraState {
  resumo = $state<ResumoCarteira | null>(null)
  posicoes = $state<Posicao[]>([])
  operacoes = $state<Operacao[]>([])
  serie = $state<SerieRentabilidade | null>(null)
  ativos = $state<Ativo[]>([])
  fonte = $state<'api' | 'simulada'>('simulada')
  atualizadoEm = $state<Date | null>(null)
  carregando = $state(false)

  async carregar(): Promise<void> {
    this.carregando = true
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
      this.fonte = 'api'
    } catch {
      this.#aplicarMock()
    } finally {
      this.carregando = false
    }
  }

  async registrar(op: NovaOperacao): Promise<void> {
    if (this.fonte === 'simulada') {
      registrarOperacaoMock(op)
      this.#aplicarMock()
      return
    }
    await registrarOperacao(op)
    await this.carregar()
  }

  async atualizarCotacoes(): Promise<void> {
    if (this.fonte === 'simulada') {
      atualizarCotacoesMock()
      this.#aplicarMock()
    } else {
      await atualizarCotacoes()
      await this.carregar()
    }
    this.atualizadoEm = new Date()
  }

  #aplicarMock(): void {
    const snap = snapshotMock()
    this.resumo = snap.resumo
    this.posicoes = snap.posicoes
    this.operacoes = snap.operacoes
    this.serie = snap.serie
    this.ativos = snap.ativos
    this.fonte = 'simulada'
  }
}

export const carteira = new CarteiraState()
