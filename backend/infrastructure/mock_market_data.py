"""Provedor de cotações SIMULADO — implementa core.ports.ProvedorCotacoes.

Substitui temporariamente os clientes reais de infrastructure/market_data/
(brapi e BCB). Os dados são: cotações base,
séries acumuladas de 12 meses e uma variação aleatória pequena a cada
atualização, partindo da última cotação persistida.
"""

import random
from datetime import date
from decimal import Decimal

from core.entities import Ativo, ClasseAtivo
from portfolio.models import Cotacao

COTACOES_BASE: dict[str, Decimal] = {
    "PETR4": Decimal("41.87"),
    "VALE3": Decimal("63.40"),
    "ITUB4": Decimal("38.12"),
    "WEGE3": Decimal("42.75"),
    "BBAS3": Decimal("29.34"),
    "KNRI11": Decimal("165.20"),
    "MXRF11": Decimal("10.42"),
    "TSELIC29": Decimal("15834.22"),
}

FECHAMENTO_ANTERIOR: dict[str, Decimal] = {
    "PETR4": Decimal("41.52"),
    "VALE3": Decimal("63.95"),
    "ITUB4": Decimal("37.88"),
    "WEGE3": Decimal("42.60"),
    "BBAS3": Decimal("29.10"),
    "KNRI11": Decimal("164.80"),
    "MXRF11": Decimal("10.40"),
    "TSELIC29": Decimal("15827.10"),
}

# 13 meses: ponto-base (0%) + 12 retornos mensais, como a janela padrão
# de CalcularRentabilidade (meses=12).
_MESES = [
    date(2025, 6, 1), date(2025, 7, 1), date(2025, 8, 1), date(2025, 9, 1),
    date(2025, 10, 1), date(2025, 11, 1), date(2025, 12, 1), date(2026, 1, 1),
    date(2026, 2, 1), date(2026, 3, 1), date(2026, 4, 1), date(2026, 5, 1),
    date(2026, 6, 1),
]

SERIES: dict[str, dict[date, Decimal]] = {
    "carteira": dict(zip(_MESES, map(Decimal, "0 1.2 2.8 3.5 5.1 6.0 7.4 8.2 9.6 11.3 12.8 14.2 15.4".split()))),
    "cdi": dict(zip(_MESES, map(Decimal, "0 0.9 1.8 2.8 3.7 4.7 5.6 6.5 7.4 8.4 9.3 10.3 11.2".split()))),
    "ibovespa": dict(zip(_MESES, map(Decimal, "0 2.1 1.4 3.9 3.2 5.6 4.8 7.5 8.9 10.2 11.6 12.4 13.5".split()))),
}


class MockProvedorCotacoes:
    def cotacao_atual(self, ticker: str) -> Decimal:
        ultima = (
            Cotacao.objects.filter(ativo__ticker=ticker)
            .values_list("preco", flat=True)
            .first()
        ) or COTACOES_BASE.get(ticker, Decimal("0"))
        drift = Decimal("0.0004") if ticker == "TSELIC29" else Decimal(
            str((random.random() - 0.48) * 0.012)
        )
        return (ultima * (1 + drift)).quantize(Decimal("0.01"))

    def fechamento_anterior(self, ticker: str) -> Decimal | None:
        armazenado = (
            Cotacao.objects.filter(ativo__ticker=ticker)
            .values_list("fechamento_anterior", flat=True)
            .first()
        )
        return armazenado or FECHAMENTO_ANTERIOR.get(ticker)

    def serie_indice(self, indice: str, inicio: date, fim: date) -> dict[date, Decimal]:
        serie = SERIES.get(indice, {})
        return {d: v for d, v in serie.items() if inicio <= d <= fim}

    def buscar_ativo(self, ticker: str) -> Ativo | None:
        """No mock, qualquer ticker com cotação base é 'conhecido pela B3'."""
        ticker = ticker.upper()
        if ticker not in COTACOES_BASE:
            return None
        classe = ClasseAtivo.FII if ticker.endswith("11") else ClasseAtivo.ACAO
        return Ativo(ticker=ticker, nome=ticker, classe=classe)

    def serie_precos(self, ticker: str, inicio: date, fim: date) -> dict[date, Decimal]:
        # O mock fornece a série 'carteira' pronta em serie_indice, então o
        # domínio não precisa de preços históricos simulados.
        return {}
