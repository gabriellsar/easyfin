"""Caso de uso: séries acumuladas de rentabilidade da carteira vs. benchmarks.

CDI e Ibovespa vêm do ProvedorCotacoes. A série da carteira:
- se o provedor a fornece pronta (MockProvedorCotacoes), é usada direto;
- caso contrário (provedor real), é CALCULADA aqui a partir das operações e
  dos fechamentos mensais (serie_precos).

Regras do cálculo mensal:
- `meses` é o número de retornos mensais compostos: a série tem meses + 1
  pontos, com base 0% no primeiro (fim do mês anterior à janela).
- Retorno do mês por Dietz modificado com aportes (compras) ponderados no
  início do mês e resgates (vendas) no fim:
  (V_fim + vendas - V_ini - compras) / (V_ini + compras).
- Tickers sem histórico de preços na fonte (ex.: títulos do Tesouro) são
  avaliados pelo custo médio das compras feitas até o mês — contribuição de
  retorno zero enquanto mantidos; vendas realizam o resultado no mês em que
  ocorrem. Aproximação documentada até existir fonte de preços de renda fixa.
"""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import TypedDict

from core.entities import Operacao, TipoOperacao
from core.ports import ProvedorCotacoes, RepositorioOperacoes

INDICES_SUPORTADOS = ("cdi", "ibovespa")


class SerieRentabilidade(TypedDict):
    datas: list[date]
    carteira: list[float]
    indices: dict[str, list[float]]


def _primeiro_do_mes_ha(meses_atras: int, referencia: date) -> date:
    total = referencia.year * 12 + (referencia.month - 1) - meses_atras
    return date(total // 12, total % 12 + 1, 1)


def _proximo_mes(mes: date) -> date:
    return date(mes.year + 1, 1, 1) if mes.month == 12 else date(mes.year, mes.month + 1, 1)


class CalcularRentabilidade:
    def __init__(
        self,
        repo_operacoes: RepositorioOperacoes,
        provedor: ProvedorCotacoes,
    ) -> None:
        self._repo_operacoes = repo_operacoes
        self._provedor = provedor

    def executar(
        self,
        meses: int = 12,
        indices: Sequence[str] = ("cdi", "ibovespa"),
        hoje: date | None = None,
    ) -> SerieRentabilidade:
        hoje = hoje or date.today()
        fim = _primeiro_do_mes_ha(1, hoje)  # mês fechado mais recente
        inicio = _primeiro_do_mes_ha(meses + 1, hoje)  # ponto-base (0%) da janela

        datas: list[date] = []
        mes = inicio
        while mes <= fim:
            datas.append(mes)
            mes = _proximo_mes(mes)

        carteira = self._provedor.serie_indice("carteira", inicio, fim)
        if not carteira:
            carteira = self._serie_carteira(datas)

        series = {i: self._provedor.serie_indice(i, inicio, fim) for i in indices}

        return SerieRentabilidade(
            datas=datas,
            carteira=[float(carteira.get(d, 0)) for d in datas],
            indices={
                i: [float(s.get(d, 0)) for d in datas] for i, s in series.items()
            },
        )

    # ---------- série da carteira (Dietz modificado mensal) ----------

    def _serie_carteira(self, datas: list[date]) -> dict[date, Decimal]:
        operacoes = sorted(self._repo_operacoes.listar_todas(), key=lambda o: o.data)
        if not operacoes or not datas:
            return {}

        inicio, fim = datas[0], datas[-1]
        tickers = {op.ticker for op in operacoes}
        precos = {t: self._provedor.serie_precos(t, inicio, fim) for t in tickers}

        serie: dict[date, Decimal] = {inicio: Decimal("0")}
        acumulado = Decimal("0")
        valor_anterior = self._valor_no_mes(operacoes, precos, inicio)

        for mes in datas[1:]:
            valor = self._valor_no_mes(operacoes, precos, mes)
            compras, vendas = _fluxos_do_mes(operacoes, mes)
            base = valor_anterior + compras
            retorno = (
                (valor + vendas - valor_anterior - compras) / base
                if base > 0
                else Decimal("0")
            )
            acumulado = ((1 + acumulado / 100) * (1 + retorno) - 1) * 100
            serie[mes] = acumulado
            valor_anterior = valor
        return serie

    def _valor_no_mes(
        self,
        operacoes: list[Operacao],
        precos: dict[str, dict[date, Decimal]],
        mes: date,
    ) -> Decimal:
        corte = _proximo_mes(mes)
        quantidades: dict[str, Decimal] = {}
        for op in operacoes:
            if op.data >= corte:
                break
            sinal = 1 if op.tipo == TipoOperacao.COMPRA else -1
            quantidades[op.ticker] = quantidades.get(op.ticker, Decimal("0")) + sinal * op.quantidade

        total = Decimal("0")
        for ticker, qtd in quantidades.items():
            if qtd <= 0:
                continue
            preco = _preco_ate_o_mes(precos.get(ticker, {}), mes)
            if preco is None:
                preco = _preco_medio_compras(operacoes, ticker, corte)
            total += qtd * preco
        return total


def _fluxos_do_mes(operacoes: list[Operacao], mes: date) -> tuple[Decimal, Decimal]:
    """Total financeiro de compras e de vendas do mês (ambos positivos)."""
    corte = _proximo_mes(mes)
    compras = Decimal("0")
    vendas = Decimal("0")
    for op in operacoes:
        if mes <= op.data < corte:
            if op.tipo == TipoOperacao.COMPRA:
                compras += op.valor_total
            else:
                vendas += op.valor_total
    return compras, vendas


def _preco_ate_o_mes(precos: dict[date, Decimal], mes: date) -> Decimal | None:
    """Fechamento do mês, ou o último conhecido antes dele."""
    candidatos = [d for d in precos if d <= mes]
    return precos[max(candidatos)] if candidatos else None


def _preco_medio_compras(operacoes: list[Operacao], ticker: str, ate: date) -> Decimal:
    """Custo médio das compras anteriores a `ate` — sem olhar preços futuros."""
    compras = [
        o
        for o in operacoes
        if o.ticker == ticker and o.tipo == TipoOperacao.COMPRA and o.data < ate
    ]
    quantidade = sum((o.quantidade for o in compras), Decimal("0"))
    if quantidade == 0:
        return Decimal("0")
    return sum((o.valor_total for o in compras), Decimal("0")) / quantidade
