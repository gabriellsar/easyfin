"""Cliente brapi.dev — cotações de ativos B3 e do Ibovespa (^BVSP).

Implementa parte do port ProvedorCotacoes (core/ports.py).
Docs: https://brapi.dev/docs
"""

import os
from decimal import Decimal

import requests

BRAPI_BASE_URL = "https://brapi.dev/api"


class BrapiClient:
    def __init__(self, token: str | None = None) -> None:
        self._token = token or os.getenv("BRAPI_TOKEN", "")

    def cotacao_atual(self, ticker: str) -> Decimal:
        # TODO(passo 4): GET /quote/{ticker} e extrair regularMarketPrice.
        raise NotImplementedError
