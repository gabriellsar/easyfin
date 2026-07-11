"""Montagem dos casos de uso com as implementações concretas.

Único ponto que conhece infraestrutura E domínio. Quando os clientes reais
brapi/BCB ficarem prontos (infrastructure/market_data/), basta trocar
MockProvedorCotacoes aqui.
"""

from core.use_cases.atualizar_cotacoes import AtualizarCotacoes
from core.use_cases.calcular_rentabilidade import CalcularRentabilidade
from core.use_cases.consolidar_posicoes import ConsolidarPosicoes
from core.use_cases.gerar_relatorio_excel import GerarRelatorioExcel
from core.use_cases.registrar_operacao import RegistrarOperacao
from core.use_cases.resumo_carteira import ResumoCarteira
from infrastructure.excel.openpyxl_writer import OpenpyxlWriter
from infrastructure.mock_market_data import MockProvedorCotacoes
from portfolio.repositories import (
    RepositorioAtivosDjango,
    RepositorioCotacoesDjango,
    RepositorioOperacoesDjango,
)


def registrar_operacao() -> RegistrarOperacao:
    return RegistrarOperacao(RepositorioAtivosDjango(), RepositorioOperacoesDjango())


def consolidar_posicoes() -> ConsolidarPosicoes:
    return ConsolidarPosicoes(
        RepositorioAtivosDjango(),
        RepositorioOperacoesDjango(),
        RepositorioCotacoesDjango(),
    )


def calcular_rentabilidade() -> CalcularRentabilidade:
    return CalcularRentabilidade(RepositorioOperacoesDjango(), MockProvedorCotacoes())


def resumo_carteira() -> ResumoCarteira:
    return ResumoCarteira(
        consolidar_posicoes(), RepositorioCotacoesDjango(), calcular_rentabilidade()
    )


def atualizar_cotacoes() -> AtualizarCotacoes:
    return AtualizarCotacoes(
        RepositorioAtivosDjango(), MockProvedorCotacoes(), RepositorioCotacoesDjango()
    )


def gerar_relatorio_excel() -> GerarRelatorioExcel:
    return GerarRelatorioExcel(
        consolidar_posicoes(), RepositorioOperacoesDjango(), OpenpyxlWriter()
    )
