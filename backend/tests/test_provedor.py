"""Testes da composição de fontes no ProvedorCotacoesB3Bcb — com clientes
fake, sem rede. O contrato coberto: Yahoo é a fonte primária de histórico,
brapi é contingência, e o Ibovespa é derivado do histórico do ^BVSP."""

from datetime import date
from decimal import Decimal

from core.entities import FonteExternaError
from infrastructure.market_data.provedor import ProvedorCotacoesB3Bcb

INICIO = date(2026, 4, 1)
FIM = date(2026, 6, 1)


class YahooFake:
    def __init__(self, series=None, erro=False):
        self._series = series or {}
        self._erro = erro

    def serie_precos(self, ticker, inicio, fim):
        if self._erro:
            raise FonteExternaError("Yahoo fora do ar")
        return self._series.get(ticker, {})


class BrapiFake:
    def __init__(self, series=None):
        self._series = series or {}

    def serie_precos(self, ticker, inicio, fim):
        return self._series.get(ticker, {})


SERIE_YAHOO = {INICIO: Decimal("10"), FIM: Decimal("12")}
SERIE_BRAPI = {FIM: Decimal("11")}


def _provedor(yahoo, brapi=None):
    return ProvedorCotacoesB3Bcb(brapi=brapi or BrapiFake(), bcb=None, yahoo=yahoo)


def test_historico_vem_do_yahoo_quando_disponivel():
    provedor = _provedor(
        YahooFake({"PETR4": SERIE_YAHOO}), BrapiFake({"PETR4": SERIE_BRAPI})
    )
    assert provedor.serie_precos("PETR4", INICIO, FIM) == SERIE_YAHOO


def test_brapi_cobre_quando_yahoo_falha():
    provedor = _provedor(YahooFake(erro=True), BrapiFake({"PETR4": SERIE_BRAPI}))
    assert provedor.serie_precos("PETR4", INICIO, FIM) == SERIE_BRAPI


def test_brapi_cobre_quando_yahoo_nao_conhece_o_ticker():
    provedor = _provedor(YahooFake(), BrapiFake({"PETR4": SERIE_BRAPI}))
    assert provedor.serie_precos("PETR4", INICIO, FIM) == SERIE_BRAPI


def test_ticker_desconhecido_das_duas_fontes_retorna_vazio():
    provedor = _provedor(YahooFake(), BrapiFake())
    assert provedor.serie_precos("TSELIC29", INICIO, FIM) == {}


def test_ibovespa_e_acumulado_a_partir_do_historico():
    provedor = _provedor(
        YahooFake({"^BVSP": {INICIO: Decimal("100000"), FIM: Decimal("110000")}})
    )
    serie = provedor.serie_indice("ibovespa", INICIO, FIM)
    assert serie[INICIO] == 0
    assert serie[FIM] == Decimal("10")


def test_serie_carteira_nao_e_fornecida():
    provedor = _provedor(YahooFake())
    assert provedor.serie_indice("carteira", INICIO, FIM) == {}
