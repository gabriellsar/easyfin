"""Cliente Yahoo Finance — histórico mensal de preços (API não oficial).

Complementa a brapi, cujo plano gratuito limita o histórico aos últimos
3 meses: o endpoint /v8/finance/chart aceita janelas arbitrárias
(period1/period2), o que dá os 12+ meses de que a rentabilidade precisa.

- Tickers da B3 são consultados com o sufixo .SA; índices (^BVSP) como estão.
- Tickers desconhecidos (ex.: títulos do Tesouro) retornam série vazia.
- Respostas são cacheadas em memória por 10 minutos.
"""

import time
from datetime import date, datetime, timezone
from decimal import Decimal

import requests

from core.entities import FonteExternaError

YAHOO_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
_CACHE_TTL_SEGUNDOS = 600
# sem User-Agent de navegador o Yahoo recusa a requisição
_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"


def _simbolo(ticker: str) -> str:
    return ticker if ticker.startswith("^") else f"{ticker.upper()}.SA"


def _proximo_mes(mes: date) -> date:
    return date(mes.year + 1, 1, 1) if mes.month == 12 else date(mes.year, mes.month + 1, 1)


def _em(valores: list, i: int):
    return valores[i] if i < len(valores) else None


class YahooFinanceClient:
    def __init__(self, timeout: int = 15) -> None:
        self._timeout = timeout
        self._cache: dict[str, tuple[float, dict[date, Decimal]]] = {}
        self._session = requests.Session()
        self._session.headers["User-Agent"] = _USER_AGENT

    def serie_precos(self, ticker: str, inicio: date, fim: date) -> dict[date, Decimal]:
        """Fechamentos mensais ajustados (chave = 1º dia do mês), como o port."""
        chave = f"{ticker}|{inicio}|{fim}"
        em_cache = self._cache.get(chave)
        if em_cache and time.monotonic() - em_cache[0] < _CACHE_TTL_SEGUNDOS:
            return em_cache[1]

        serie = self._buscar(ticker, inicio, fim)
        self._cache[chave] = (time.monotonic(), serie)
        return serie

    def _buscar(self, ticker: str, inicio: date, fim: date) -> dict[date, Decimal]:
        depois_do_fim = _proximo_mes(fim)  # period2 é exclusivo
        params = {
            "period1": int(datetime(inicio.year, inicio.month, 1, tzinfo=timezone.utc).timestamp()),
            "period2": int(
                datetime(depois_do_fim.year, depois_do_fim.month, 1, tzinfo=timezone.utc).timestamp()
            ),
            "interval": "1mo",
        }
        try:
            resp = self._session.get(
                f"{YAHOO_BASE_URL}/{_simbolo(ticker)}", params=params, timeout=self._timeout
            )
        except requests.RequestException as e:
            raise FonteExternaError(f"Yahoo Finance indisponível: {e}") from e

        if resp.status_code == 404:
            return {}  # ticker desconhecido pelo Yahoo (ex.: Tesouro Direto)
        if not resp.ok:
            raise FonteExternaError(f"Yahoo Finance respondeu HTTP {resp.status_code}")

        resultado = ((resp.json().get("chart") or {}).get("result") or [None])[0]
        if not resultado:
            return {}
        timestamps = resultado.get("timestamp") or []
        indicadores = resultado.get("indicators") or {}
        ajustados = (indicadores.get("adjclose") or [{}])[0].get("adjclose") or []
        fechamentos = (indicadores.get("quote") or [{}])[0].get("close") or []

        serie: dict[date, Decimal] = {}
        for i, ts in enumerate(timestamps):
            preco = _em(ajustados, i)
            if preco is None:
                preco = _em(fechamentos, i)
            if preco is None:
                continue
            mes = datetime.fromtimestamp(ts, tz=timezone.utc).date().replace(day=1)
            if inicio <= mes <= fim:
                serie[mes] = Decimal(str(preco))
        return serie
