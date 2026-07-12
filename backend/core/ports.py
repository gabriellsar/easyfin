"""Ports (contratos) que o domínio exige da infraestrutura."""

from datetime import date
from decimal import Decimal
from typing import Protocol

from core.entities import Ativo, Operacao, Posicao


class RepositorioAtivos(Protocol):
    def buscar_por_ticker(self, ticker: str) -> Ativo | None: ...

    def listar(self) -> list[Ativo]: ...

    def salvar(self, ativo: Ativo) -> Ativo: ...


class RepositorioOperacoes(Protocol):
    def salvar(self, operacao: Operacao) -> Operacao: ...

    def listar_por_ticker(self, ticker: str) -> list[Operacao]: ...

    def listar_todas(self) -> list[Operacao]: ...


class RepositorioCotacoes(Protocol):
    """Última cotação conhecida de cada ativo (marcação a mercado persistida)."""

    def cotacao_atual(self, ticker: str) -> Decimal | None: ...

    def fechamento_anterior(self, ticker: str) -> Decimal | None: ...

    def salvar(
        self, ticker: str, preco: Decimal, fechamento_anterior: Decimal | None = None
    ) -> None: ...


class ProvedorCotacoes(Protocol):
    """Fonte externa de cotações (brapi para cotação atual, Yahoo Finance
    para histórico mensal, BCB para CDI).

    Selecionada em api/deps.py via MARKET_DATA_PROVIDER:
    ProvedorCotacoesB3Bcb (real) ou MockProvedorCotacoes.
    """

    def cotacao_atual(self, ticker: str) -> Decimal | None:
        """Preço atual, ou None se a fonte não conhece o ticker."""
        ...

    def fechamento_anterior(self, ticker: str) -> Decimal | None: ...

    def buscar_ativo(self, ticker: str) -> Ativo | None:
        """Metadados (nome/classe) de um ticker, ou None se não existe na fonte."""
        ...

    def serie_indice(self, indice: str, inicio: date, fim: date) -> dict[date, Decimal]:
        """Série mensal acumulada em % (base 0 no primeiro mês) de um índice
        ('cdi', 'ibovespa', 'carteira'). Vazia se indisponível."""
        ...

    def serie_precos(self, ticker: str, inicio: date, fim: date) -> dict[date, Decimal]:
        """Fechamentos mensais ajustados do ticker (chave = 1º dia do mês)."""
        ...


class GeradorRelatorio(Protocol):
    def gerar(self, posicoes: list[Posicao], operacoes: list[Operacao]) -> bytes: ...
