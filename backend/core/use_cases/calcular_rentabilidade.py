"""Caso de uso: séries acumuladas de rentabilidade da carteira vs. benchmarks
(CDI via BCB/SGS, Ibovespa via brapi)."""

from datetime import date
from decimal import Decimal
from typing import TypedDict

from core.ports import ProvedorCotacoes, RepositorioOperacoes


class SerieRentabilidade(TypedDict):
    datas: list[date]
    carteira: list[Decimal]
    cdi: list[Decimal]
    ibovespa: list[Decimal]


class CalcularRentabilidade:
    def __init__(
        self,
        repo_operacoes: RepositorioOperacoes,
        cotacoes: ProvedorCotacoes,
    ) -> None:
        self._repo_operacoes = repo_operacoes
        self._cotacoes = cotacoes

    def executar(self, meses: int = 12) -> SerieRentabilidade:
        # TODO(passo 4): calcular série acumulada da carteira e comparar
        # com CDI e Ibovespa no mesmo período.
        raise NotImplementedError
