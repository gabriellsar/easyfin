"""Cliente da API SGS do Banco Central — séries de CDI e SELIC.

Implementa a parte de índices de renda fixa do port ProvedorCotacoes.
Séries SGS mensais (% a.m.): CDI = 4391, SELIC = 4390.
Docs: https://dadosabertos.bcb.gov.br — API aberta, sem autenticação.
Respostas são cacheadas em memória por 10 minutos.
"""

import time
from datetime import date
from decimal import Decimal

import requests

from core.entities import FonteExternaError

SGS_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"

SERIES = {
    "cdi": 4391,
    "selic": 4390,
}

_CACHE_TTL_SEGUNDOS = 600


def _proximo_mes(mes: date) -> date:
    return date(mes.year + 1, 1, 1) if mes.month == 12 else date(mes.year, mes.month + 1, 1)


class BcbClient:
    def __init__(self, timeout: int = 15) -> None:
        self._timeout = timeout
        self._cache: dict[str, tuple[float, list[dict]]] = {}

    def _dados(self, codigo: int, inicio: date, fim: date) -> list[dict]:
        chave = f"{codigo}|{inicio}|{fim}"
        em_cache = self._cache.get(chave)
        if em_cache and time.monotonic() - em_cache[0] < _CACHE_TTL_SEGUNDOS:
            return em_cache[1]

        try:
            resp = requests.get(
                SGS_BASE_URL.format(codigo=codigo),
                params={
                    "formato": "json",
                    "dataInicial": inicio.strftime("%d/%m/%Y"),
                    "dataFinal": fim.strftime("%d/%m/%Y"),
                },
                timeout=self._timeout,
            )
            resp.raise_for_status()
            dados = resp.json()
        except (requests.RequestException, ValueError) as e:
            raise FonteExternaError(f"API SGS do BCB indisponível: {e}") from e

        self._cache[chave] = (time.monotonic(), dados)
        return dados

    def serie_indice(self, indice: str, inicio: date, fim: date) -> dict[date, Decimal]:
        """Série mensal ACUMULADA em %, base 0 no mês `inicio` — composta a
        partir das taxas mensais (% a.m.) da série SGS."""
        codigo = SERIES.get(indice)
        if codigo is None:
            return {}

        # taxas dos meses seguintes ao mês-base (o mês-base é o ponto zero)
        primeiro_com_taxa = _proximo_mes(inicio)
        ultimo_dia = _proximo_mes(fim)  # exclusivo
        dados = self._dados(codigo, primeiro_com_taxa, ultimo_dia)

        taxas: dict[date, Decimal] = {}
        for item in dados:
            _, mes_str, ano = item["data"].split("/")
            taxas[date(int(ano), int(mes_str), 1)] = Decimal(item["valor"])

        serie: dict[date, Decimal] = {inicio: Decimal("0")}
        fator = Decimal("1")
        mes = primeiro_com_taxa
        while mes <= fim:
            fator *= 1 + taxas.get(mes, Decimal("0")) / 100
            serie[mes] = (fator - 1) * 100
            mes = _proximo_mes(mes)
        return serie
