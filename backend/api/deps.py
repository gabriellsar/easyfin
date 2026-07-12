"""Montagem dos casos de uso com as implementações concretas.

Único ponto que conhece infraestrutura E domínio. O provedor de cotações é
escolhido pela variável de ambiente MARKET_DATA_PROVIDER:
- "real" (padrão): brapi + Banco Central (infrastructure/market_data/)
- "mock": dados simulados (infrastructure/mock_market_data.py) — usado nos
  testes para não depender de rede.
"""

import os

from core.ports import ProvedorCotacoes
from core.use_cases.atualizar_cotacoes import AtualizarCotacoes
from core.use_cases.calcular_rentabilidade import CalcularRentabilidade
from core.use_cases.consolidar_posicoes import ConsolidarPosicoes
from core.use_cases.gerar_relatorio_excel import GerarRelatorioExcel
from core.use_cases.registrar_operacao import RegistrarOperacao
from core.use_cases.resumo_carteira import ResumoCarteira
from infrastructure.excel.openpyxl_writer import OpenpyxlWriter
from infrastructure.market_data.provedor import ProvedorCotacoesB3Bcb
from infrastructure.mock_market_data import MockProvedorCotacoes
from portfolio.repositories import (
    RepositorioAtivosDjango,
    RepositorioCotacoesDjango,
    RepositorioOperacoesDjango,
)


def provedor_cotacoes() -> ProvedorCotacoes:
    if os.getenv("MARKET_DATA_PROVIDER", "real") == "mock":
        return MockProvedorCotacoes()
    return ProvedorCotacoesB3Bcb()


def registrar_operacao(usuario) -> RegistrarOperacao:
    return RegistrarOperacao(
        RepositorioAtivosDjango(),
        RepositorioOperacoesDjango(usuario),
        provedor_cotacoes(),
        RepositorioCotacoesDjango(),
    )


def consolidar_posicoes(usuario) -> ConsolidarPosicoes:
    return ConsolidarPosicoes(
        RepositorioAtivosDjango(),
        RepositorioOperacoesDjango(usuario),
        RepositorioCotacoesDjango(),
    )


def calcular_rentabilidade(usuario) -> CalcularRentabilidade:
    return CalcularRentabilidade(RepositorioOperacoesDjango(usuario), provedor_cotacoes())


def resumo_carteira(usuario) -> ResumoCarteira:
    return ResumoCarteira(
        consolidar_posicoes(usuario),
        RepositorioCotacoesDjango(),
        calcular_rentabilidade(usuario),
    )


def atualizar_cotacoes() -> AtualizarCotacoes:
    # Cotações são dados de mercado, globais — não têm dono.
    return AtualizarCotacoes(
        RepositorioAtivosDjango(), provedor_cotacoes(), RepositorioCotacoesDjango()
    )


def gerar_relatorio_excel(usuario) -> GerarRelatorioExcel:
    return GerarRelatorioExcel(
        consolidar_posicoes(usuario), RepositorioOperacoesDjango(usuario), OpenpyxlWriter()
    )
