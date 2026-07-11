"""Ports (contratos) que o domínio exige da infraestrutura."""

from datetime import date
from decimal import Decimal
from typing import Protocol

from core.entities import Ativo, Operacao, Posicao


class RepositorioAtivos(Protocol):
    def buscar_por_ticker(self, ticker: str) -> Ativo | None: ...

    def listar(self) -> list[Ativo]: ...


class RepositorioOperacoes(Protocol):
    def salvar(self, operacao: Operacao) -> Operacao: ...

    def listar_por_ticker(self, ticker: str) -> list[Operacao]: ...

    def listar_todas(self) -> list[Operacao]: ...


class RepositorioCotacoes(Protocol):
    """Última cotação conhecida de cada ativo (marcação a mercado persistida)."""

    def cotacao_atual(self, ticker: str) -> Decimal | None: ...

    def fechamento_anterior(self, ticker: str) -> Decimal | None: ...

    def salvar(self, ticker: str, preco: Decimal) -> None: ...


class ProvedorCotacoes(Protocol):
    """Fonte externa de cotações (brapi para B3/IBOV, BCB para CDI/SELIC).

    Hoje implementado por MockProvedorCotacoes; os clientes reais em
    infrastructure/market_data/ o substituirão sem mudar o domínio.
    """

    def cotacao_atual(self, ticker: str) -> Decimal: ...

    def serie_indice(self, indice: str, inicio: date, fim: date) -> dict[date, Decimal]: ...


class GeradorRelatorio(Protocol):
    def gerar(self, posicoes: list[Posicao], operacoes: list[Operacao]) -> bytes: ...
