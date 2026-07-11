"""Cliente da API SGS do Banco Central — séries de CDI e SELIC.

Implementa parte do port ProvedorCotacoes (core/ports.py).
Séries SGS: CDI diário = 12, SELIC diária = 11.
Docs: https://dadosabertos.bcb.gov.br
"""

from datetime import date
from decimal import Decimal

import requests

SGS_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

SERIES = {
    "cdi": 12,
    "selic": 11,
}


class BcbClient:
    def serie_indice(self, indice: str, inicio: date, fim: date) -> dict[date, Decimal]:
        # TODO(passo 4): GET na série SGS com dataInicial/dataFinal (dd/MM/yyyy)
        # e converter para {date: Decimal}.
        raise NotImplementedError
