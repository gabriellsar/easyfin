"""Caso de uso: séries acumuladas de rentabilidade da carteira vs. benchmarks.

CDI e Ibovespa vêm do ProvedorCotacoes. A série da carteira:
- se o provedor a fornece pronta (MockProvedorCotacoes), é usada direto;
- caso contrário (provedor real), é CALCULADA aqui a partir das operações e
  dos fechamentos mensais (serie_precos), com retorno de Dietz simples por
  mês composto ao longo do período.

Tickers sem histórico de preços na fonte (ex.: títulos do Tesouro) entram
pelo preço médio de compra (contribuição de retorno zero) — aproximação
documentada até existir uma fonte de preços de renda fixa.
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
        inicio = _primeiro_do_mes_ha(meses, hoje)

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

    # ---------- série da carteira (Dietz simples mensal) ----------

    def _serie_carteira(self, datas: list[date]) -> dict[date, Decimal]:
        operacoes = sorted(self._repo_operacoes.listar_todas(), key=lambda o: o.data)
        if not operacoes or not datas:
            return {}

        inicio, fim = datas[0], datas[-1]
        tickers = {op.ticker for op in operacoes}
        precos = {t: self._provedor.serie_precos(t, inicio, fim) for t in tickers}
        preco_fallback = {t: _preco_medio_compras(operacoes, t) for t in tickers}

        serie: dict[date, Decimal] = {inicio: Decimal("0")}
        acumulado = Decimal("0")
        valor_anterior = self._valor_no_mes(operacoes, precos, preco_fallback, inicio)

        for mes in datas[1:]:
            valor = self._valor_no_mes(operacoes, precos, preco_fallback, mes)
            fluxo = _fluxo_do_mes(operacoes, mes)
            base = valor_anterior + fluxo
            retorno = (valor - valor_anterior - fluxo) / base if base > 0 else Decimal("0")
            acumulado = ((1 + acumulado / 100) * (1 + retorno) - 1) * 100
            serie[mes] = acumulado
            valor_anterior = valor
        return serie

    def _valor_no_mes(
        self,
        operacoes: list[Operacao],
        precos: dict[str, dict[date, Decimal]],
        preco_fallback: dict[str, Decimal],
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
            preco = _preco_ate_o_mes(precos.get(ticker, {}), mes) or preco_fallback[ticker]
            total += qtd * preco
        return total


def _fluxo_do_mes(operacoes: list[Operacao], mes: date) -> Decimal:
    """Aportes líquidos no mês: compras entram (+), vendas saem (-)."""
    corte = _proximo_mes(mes)
    fluxo = Decimal("0")
    for op in operacoes:
        if mes <= op.data < corte:
            sinal = 1 if op.tipo == TipoOperacao.COMPRA else -1
            fluxo += sinal * op.valor_total
    return fluxo


def _preco_ate_o_mes(precos: dict[date, Decimal], mes: date) -> Decimal | None:
    """Fechamento do mês, ou o último conhecido antes dele."""
    candidatos = [d for d in precos if d <= mes]
    return precos[max(candidatos)] if candidatos else None


def _preco_medio_compras(operacoes: list[Operacao], ticker: str) -> Decimal:
    compras = [o for o in operacoes if o.ticker == ticker and o.tipo == TipoOperacao.COMPRA]
    quantidade = sum((o.quantidade for o in compras), Decimal("0"))
    if quantidade == 0:
        return Decimal("0")
    return sum((o.valor_total for o in compras), Decimal("0")) / quantidade
