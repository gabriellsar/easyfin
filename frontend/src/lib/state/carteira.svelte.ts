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
import { INDICES_DISPONIVEIS } from '../utils/format'

const INDICES_KEY = 'easyfin.indices'
const INDICES_PADRAO = ['ibovespa', 'cdi']

function lerIndicesSalvos(): string[] {
  try {
    const salvo = JSON.parse(localStorage.getItem(INDICES_KEY) ?? '')
    if (Array.isArray(salvo)) {
      const validos = salvo.filter((i) => (INDICES_DISPONIVEIS as readonly string[]).includes(i))
      if (validos.length > 0) return validos
    }
  } catch {
    /* primeiro acesso */
  }
  return [...INDICES_PADRAO]
}

class CarteiraState {
  resumo = $state<ResumoCarteira | null>(null)
  posicoes = $state<Posicao[]>([])
  operacoes = $state<Operacao[]>([])
  serie = $state<SerieRentabilidade | null>(null)
  ativos = $state<Ativo[]>([])
  indicesSelecionados = $state<string[]>(lerIndicesSalvos())
  atualizadoEm = $state<Date | null>(null)
  carregando = $state(false)
  erro = $state<string | null>(null)

  // descarta respostas de série que chegam fora de ordem (toggles rápidos)
  #serieRequisicao = 0

  async carregar(): Promise<void> {
    this.carregando = true
    this.erro = null
    try {
      const [posicoes, operacoes, ativos] = await Promise.all([
        listarPosicoes(),
        listarOperacoes(),
        listarAtivos(),
      ])
      this.posicoes = posicoes
      this.operacoes = operacoes.results
      this.ativos = ativos.results
    } catch {
      this.erro = 'Não foi possível carregar os dados da carteira.'
      this.carregando = false
      return
    }

    // KPIs e séries dependem de fontes externas (brapi/BCB); falha aqui não
    // derruba a tela — os cards exibem "—" até a próxima tentativa.
    const requisicao = ++this.#serieRequisicao
    const [resumo, serie] = await Promise.allSettled([
      obterResumo(),
      obterRentabilidade(12, this.indicesSelecionados),
    ])
    this.resumo = resumo.status === 'fulfilled' ? resumo.value : null
    if (requisicao === this.#serieRequisicao) {
      this.serie = serie.status === 'fulfilled' ? serie.value : null
    }
    this.carregando = false
  }

  async alternarIndice(indice: string): Promise<void> {
    this.indicesSelecionados = this.indicesSelecionados.includes(indice)
      ? this.indicesSelecionados.filter((i) => i !== indice)
      : [...this.indicesSelecionados, indice]
    localStorage.setItem(INDICES_KEY, JSON.stringify(this.indicesSelecionados))
    const requisicao = ++this.#serieRequisicao
    try {
      const serie = await obterRentabilidade(12, this.indicesSelecionados)
      if (requisicao === this.#serieRequisicao) this.serie = serie
    } catch {
      /* mantém a série anterior */
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
