"""Entidades do domínio — puras, sem imports de Django."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum


class ClasseAtivo(str, Enum):
    ACAO = "acao"
    FII = "fii"
    RENDA_FIXA = "renda_fixa"
    ETF = "etf"


class TipoOperacao(str, Enum):
    COMPRA = "compra"
    VENDA = "venda"


@dataclass(frozen=True)
class Ativo:
    ticker: str
    nome: str
    classe: ClasseAtivo


@dataclass(frozen=True)
class Operacao:
    ticker: str
    tipo: TipoOperacao
    quantidade: Decimal
    preco_unitario: Decimal
    data: date
    id: int | None = None

    @property
    def valor_total(self) -> Decimal:
        return self.quantidade * self.preco_unitario


@dataclass
class Posicao:
    """Posição consolidada de um ativo, calculada a partir das operações."""

    ativo: Ativo
    quantidade: Decimal = Decimal("0")
    preco_medio: Decimal = Decimal("0")
    cotacao_atual: Decimal | None = None

    @property
    def custo_total(self) -> Decimal:
        return self.quantidade * self.preco_medio

    @property
    def valor_mercado(self) -> Decimal | None:
        if self.cotacao_atual is None:
            return None
        return self.quantidade * self.cotacao_atual

    @property
    def resultado(self) -> Decimal | None:
        if self.valor_mercado is None:
            return None
        return self.valor_mercado - self.custo_total

    @property
    def resultado_pct(self) -> Decimal | None:
        if self.valor_mercado is None or self.custo_total == 0:
            return None
        return (self.valor_mercado / self.custo_total - 1) * 100


class SaldoInsuficienteError(Exception):
    """Venda com quantidade maior que a disponível em carteira."""


class AtivoInexistenteError(Exception):
    """Operação sobre ticker não cadastrado."""
