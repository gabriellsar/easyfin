"""Implementações dos ports do domínio (core/ports.py) usando o ORM Django.

Convertem models <-> entidades: o domínio nunca vê um model do Django.
"""

from decimal import Decimal

from core import entities
from portfolio import models


def _ativo_para_entidade(model: models.Ativo) -> entities.Ativo:
    return entities.Ativo(
        ticker=model.ticker,
        nome=model.nome,
        classe=entities.ClasseAtivo(model.classe),
    )


def _operacao_para_entidade(model: models.Operacao) -> entities.Operacao:
    return entities.Operacao(
        id=model.pk,
        ticker=model.ativo.ticker,
        tipo=entities.TipoOperacao(model.tipo),
        quantidade=model.quantidade,
        preco_unitario=model.preco_unitario,
        data=model.data,
    )


class RepositorioAtivosDjango:
    def buscar_por_ticker(self, ticker: str) -> entities.Ativo | None:
        model = models.Ativo.objects.filter(ticker=ticker).first()
        return _ativo_para_entidade(model) if model else None

    def listar(self) -> list[entities.Ativo]:
        return [_ativo_para_entidade(m) for m in models.Ativo.objects.all()]


class RepositorioOperacoesDjango:
    """Repositório de operações ESCOPADO por usuário: cada instância enxerga
    apenas a carteira do dono. O domínio continua sem conhecer usuários."""

    def __init__(self, usuario) -> None:
        self._usuario = usuario

    def salvar(self, operacao: entities.Operacao) -> entities.Operacao:
        ativo = models.Ativo.objects.get(ticker=operacao.ticker)
        model = models.Operacao.objects.create(
            usuario=self._usuario,
            ativo=ativo,
            tipo=operacao.tipo.value,
            quantidade=operacao.quantidade,
            preco_unitario=operacao.preco_unitario,
            data=operacao.data,
        )
        return _operacao_para_entidade(model)

    def listar_por_ticker(self, ticker: str) -> list[entities.Operacao]:
        qs = models.Operacao.objects.select_related("ativo").filter(
            usuario=self._usuario, ativo__ticker=ticker
        )
        return [_operacao_para_entidade(m) for m in qs]

    def listar_todas(self) -> list[entities.Operacao]:
        qs = models.Operacao.objects.select_related("ativo").filter(usuario=self._usuario)
        return [_operacao_para_entidade(m) for m in qs]


class RepositorioCotacoesDjango:
    def cotacao_atual(self, ticker: str) -> Decimal | None:
        return (
            models.Cotacao.objects.filter(ativo__ticker=ticker)
            .values_list("preco", flat=True)
            .first()
        )

    def fechamento_anterior(self, ticker: str) -> Decimal | None:
        return (
            models.Cotacao.objects.filter(ativo__ticker=ticker)
            .values_list("fechamento_anterior", flat=True)
            .first()
        )

    def salvar(
        self, ticker: str, preco: Decimal, fechamento_anterior: Decimal | None = None
    ) -> None:
        ativo = models.Ativo.objects.get(ticker=ticker)
        defaults: dict = {"preco": preco}
        if fechamento_anterior is not None:
            defaults["fechamento_anterior"] = fechamento_anterior
        models.Cotacao.objects.update_or_create(ativo=ativo, defaults=defaults)
