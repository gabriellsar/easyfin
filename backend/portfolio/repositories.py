"""Implementações dos ports do domínio (core/ports.py) usando o ORM Django.

Convertem models <-> entidades: o domínio nunca vê um model do Django.
"""

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
    def salvar(self, operacao: entities.Operacao) -> entities.Operacao:
        # TODO(passo 2): persistir e devolver a entidade com id preenchido.
        raise NotImplementedError

    def listar_por_ticker(self, ticker: str) -> list[entities.Operacao]:
        qs = models.Operacao.objects.select_related("ativo").filter(ativo__ticker=ticker)
        return [_operacao_para_entidade(m) for m in qs]

    def listar_todas(self) -> list[entities.Operacao]:
        qs = models.Operacao.objects.select_related("ativo").all()
        return [_operacao_para_entidade(m) for m in qs]
