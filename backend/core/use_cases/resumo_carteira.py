"""Caso de uso: KPIs da visão geral — patrimônio, resultado do dia,
rentabilidade 12m e percentual do CDI."""

from decimal import Decimal
from typing import TypedDict

from core.ports import RepositorioCotacoes
from core.use_cases.calcular_rentabilidade import CalcularRentabilidade
from core.use_cases.consolidar_posicoes import ConsolidarPosicoes


class Resumo(TypedDict):
    patrimonio: Decimal
    resultado_dia: Decimal
    resultado_dia_pct: Decimal
    rentabilidade_12m: float
    percentual_cdi: float
    quantidade_posicoes: int
    quantidade_classes: int


class ResumoCarteira:
    def __init__(
        self,
        consolidar_posicoes: ConsolidarPosicoes,
        repo_cotacoes: RepositorioCotacoes,
        calcular_rentabilidade: CalcularRentabilidade,
    ) -> None:
        self._consolidar_posicoes = consolidar_posicoes
        self._repo_cotacoes = repo_cotacoes
        self._calcular_rentabilidade = calcular_rentabilidade

    def executar(self) -> Resumo:
        posicoes = self._consolidar_posicoes.executar()

        patrimonio = Decimal("0")
        resultado_dia = Decimal("0")
        for p in posicoes:
            if p.valor_mercado is not None:
                patrimonio += p.valor_mercado
            anterior = self._repo_cotacoes.fechamento_anterior(p.ativo.ticker)
            if p.cotacao_atual is not None and anterior is not None:
                resultado_dia += (p.cotacao_atual - anterior) * p.quantidade

        base_anterior = patrimonio - resultado_dia
        resultado_dia_pct = (
            resultado_dia / base_anterior * 100 if base_anterior > 0 else Decimal("0")
        )

        serie = self._calcular_rentabilidade.executar(meses=12)
        rentabilidade_12m = serie["carteira"][-1] if serie["carteira"] else 0.0
        cdi_12m = serie["cdi"][-1] if serie["cdi"] else 0.0
        percentual_cdi = rentabilidade_12m / cdi_12m * 100 if cdi_12m else 0.0

        return Resumo(
            patrimonio=patrimonio,
            resultado_dia=resultado_dia,
            resultado_dia_pct=resultado_dia_pct,
            rentabilidade_12m=rentabilidade_12m,
            percentual_cdi=percentual_cdi,
            quantidade_posicoes=len(posicoes),
            quantidade_classes=len({p.ativo.classe for p in posicoes}),
        )
