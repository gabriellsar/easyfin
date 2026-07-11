"""Cliente brapi.dev — cotações de ativos B3 e do Ibovespa (^BVSP).

Implementa a parte de ações/FIIs do port ProvedorCotacoes (core/ports.py).
Docs: https://brapi.dev/docs

Notas do plano gratuito:
- /quote/{ticker} e o histórico mensal funcionam sem token;
- ^BVSP (Ibovespa) EXIGE token (BRAPI_TOKEN no .env).
Respostas são cacheadas em memória por 10 minutos.
"""

import os
import time
from datetime import date, datetime, timezone
from decimal import Decimal

import requests

from core.entities import FonteExternaError

BRAPI_BASE_URL = "https://brapi.dev/api"
_CACHE_TTL_SEGUNDOS = 600


class BrapiClient:
    def __init__(self, token: str | None = None, timeout: int = 15) -> None:
        self._token = token or os.getenv("BRAPI_TOKEN", "")
        self._timeout = timeout
        self._cache: dict[str, tuple[float, dict]] = {}

    # ---------- HTTP ----------

    def _get_quote(self, ticker: str, params: dict | None = None) -> dict | None:
        """Retorna o primeiro result do /quote, None se o ticker não existe."""
        chave = f"{ticker}|{sorted((params or {}).items())}"
        em_cache = self._cache.get(chave)
        if em_cache and time.monotonic() - em_cache[0] < _CACHE_TTL_SEGUNDOS:
            return em_cache[1]

        query = dict(params or {})
        if self._token:
            query["token"] = self._token
        try:
            resp = requests.get(
                f"{BRAPI_BASE_URL}/quote/{ticker}", params=query, timeout=self._timeout
            )
        except requests.RequestException as e:
            raise FonteExternaError(f"brapi indisponível: {e}") from e

        if resp.status_code in (400, 401, 404):
            # ticker desconhecido pela brapi (ex.: títulos do Tesouro) ou
            # endpoint que exige token (^BVSP sem BRAPI_TOKEN)
            return None
        if not resp.ok:
            raise FonteExternaError(f"brapi respondeu HTTP {resp.status_code}")

        resultados = resp.json().get("results") or []
        resultado = resultados[0] if resultados else None
        if resultado is not None:
            self._cache[chave] = (time.monotonic(), resultado)
        return resultado

    # ---------- port ProvedorCotacoes (parte brapi) ----------

    def cotacao_atual(self, ticker: str) -> Decimal | None:
        r = self._get_quote(ticker)
        preco = r.get("regularMarketPrice") if r else None
        return Decimal(str(preco)) if preco is not None else None

    def fechamento_anterior(self, ticker: str) -> Decimal | None:
        r = self._get_quote(ticker)
        preco = r.get("regularMarketPreviousClose") if r else None
        return Decimal(str(preco)) if preco is not None else None

    def serie_precos(self, ticker: str, inicio: date, fim: date) -> dict[date, Decimal]:
        r = self._get_quote(ticker, {"range": "2y", "interval": "1mo"})
        barras = (r or {}).get("historicalDataPrice") or []
        serie: dict[date, Decimal] = {}
        for barra in barras:
            fechamento = barra.get("adjustedClose") or barra.get("close")
            if fechamento is None:
                continue
            dia = datetime.fromtimestamp(barra["date"], tz=timezone.utc).date()
            mes = dia.replace(day=1)
            if inicio <= mes <= fim:
                serie[mes] = Decimal(str(fechamento))
        return serie
