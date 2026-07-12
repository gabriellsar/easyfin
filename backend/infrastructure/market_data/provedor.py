"""ProvedorCotacoesB3Bcb — implementação REAL do port ProvedorCotacoes,
compondo três fontes:
- brapi: cotação atual e metadados de ações/FIIs;
- Yahoo Finance: histórico mensal de preços (o plano gratuito da brapi
  limita o histórico a 3 meses), com a brapi como contingência;
- Banco Central: CDI.

A série 'carteira' não é fornecida aqui de propósito: com dados reais ela é
calculada pelo caso de uso CalcularRentabilidade a partir das operações e de
serie_precos (retornar vazio sinaliza isso ao domínio).
"""

from datetime import date
from decimal import Decimal

from core.entities import Ativo, FonteExternaError
from infrastructure.market_data.bcb_client import BcbClient
from infrastructure.market_data.brapi_client import BrapiClient
from infrastructure.market_data.yahoo_client import YahooFinanceClient

TICKER_IBOVESPA = "^BVSP"


class ProvedorCotacoesB3Bcb:
    def __init__(
        self,
        brapi: BrapiClient | None = None,
        bcb: BcbClient | None = None,
        yahoo: YahooFinanceClient | None = None,
    ) -> None:
        self._brapi = brapi or BrapiClient()
        self._bcb = bcb or BcbClient()
        self._yahoo = yahoo or YahooFinanceClient()

    def cotacao_atual(self, ticker: str) -> Decimal | None:
        return self._brapi.cotacao_atual(ticker)

    def fechamento_anterior(self, ticker: str) -> Decimal | None:
        return self._brapi.fechamento_anterior(ticker)

    def buscar_ativo(self, ticker: str) -> Ativo | None:
        return self._brapi.buscar_ativo(ticker)

    def serie_precos(self, ticker: str, inicio: date, fim: date) -> dict[date, Decimal]:
        try:
            serie = self._yahoo.serie_precos(ticker, inicio, fim)
        except FonteExternaError:
            serie = {}  # Yahoo fora do ar não pode derrubar o dashboard
        return serie or self._brapi.serie_precos(ticker, inicio, fim)

    def serie_indice(self, indice: str, inicio: date, fim: date) -> dict[date, Decimal]:
        if indice == "cdi":
            return self._bcb.serie_indice(indice, inicio, fim)
        if indice == "ibovespa":
            precos = self.serie_precos(TICKER_IBOVESPA, inicio, fim)
            return _acumulada_a_partir_de_precos(precos)
        return {}  # 'carteira' é calculada no domínio


def _acumulada_a_partir_de_precos(precos: dict[date, Decimal]) -> dict[date, Decimal]:
    """Converte fechamentos mensais em série acumulada % (base 0 no 1º mês)."""
    if not precos:
        return {}
    datas = sorted(precos)
    base = precos[datas[0]]
    if base == 0:
        return {}
    return {d: (precos[d] / base - 1) * 100 for d in datas}
