"""Caso de uso: séries acumuladas de rentabilidade da carteira vs. benchmarks.

As três séries vêm do ProvedorCotacoes ('carteira', 'cdi', 'ibovespa').
TODO(integração real): quando os clientes brapi/BCB substituírem o mock,
a série da carteira passará a ser calculada aqui a partir das operações e
dos preços históricos, e apenas cdi/ibovespa virão do provedor.
"""

from datetime import date
from typing import TypedDict

from core.ports import ProvedorCotacoes, RepositorioOperacoes


class SerieRentabilidade(TypedDict):
    datas: list[date]
    carteira: list[float]
    cdi: list[float]
    ibovespa: list[float]


def _primeiro_do_mes_ha(meses_atras: int, referencia: date) -> date:
    total = referencia.year * 12 + (referencia.month - 1) - meses_atras
    return date(total // 12, total % 12 + 1, 1)


class CalcularRentabilidade:
    def __init__(
        self,
        repo_operacoes: RepositorioOperacoes,
        provedor: ProvedorCotacoes,
    ) -> None:
        self._repo_operacoes = repo_operacoes
        self._provedor = provedor

    def executar(self, meses: int = 12) -> SerieRentabilidade:
        hoje = date.today()
        fim = _primeiro_do_mes_ha(1, hoje)  # mês fechado mais recente
        inicio = _primeiro_do_mes_ha(meses, hoje)

        carteira = self._provedor.serie_indice("carteira", inicio, fim)
        cdi = self._provedor.serie_indice("cdi", inicio, fim)
        ibovespa = self._provedor.serie_indice("ibovespa", inicio, fim)

        datas = sorted(carteira)
        return SerieRentabilidade(
            datas=datas,
            carteira=[float(carteira[d]) for d in datas],
            cdi=[float(cdi.get(d, 0)) for d in datas],
            ibovespa=[float(ibovespa.get(d, 0)) for d in datas],
        )
