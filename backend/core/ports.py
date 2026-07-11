"""Ports (contratos) que o domínio exige da infraestrutura."""

from datetime import date
from decimal import Decimal
from typing import Protocol

from core.entities import Ativo, Operacao


class RepositorioAtivos(Protocol):
    def buscar_por_ticker(self, ticker: str) -> Ativo | None: ...

    def listar(self) -> list[Ativo]: ...


class RepositorioOperacoes(Protocol):
    def salvar(self, operacao: Operacao) -> Operacao: ...

    def listar_por_ticker(self, ticker: str) -> list[Operacao]: ...

    def listar_todas(self) -> list[Operacao]: ...


class ProvedorCotacoes(Protocol):
    """Cotações de mercado (brapi para B3/IBOV, BCB para CDI/SELIC)."""

    def cotacao_atual(self, ticker: str) -> Decimal: ...

    def serie_indice(self, indice: str, inicio: date, fim: date) -> dict[date, Decimal]: ...


class GeradorRelatorio(Protocol):
    def gerar(self, posicoes: list, operacoes: list[Operacao]) -> bytes: ...
