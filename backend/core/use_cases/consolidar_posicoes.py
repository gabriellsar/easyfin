"""Caso de uso: consolidar operações em posições e marcar a mercado.

Preço médio ponderado nas compras; vendas reduzem a quantidade e mantêm o
preço médio. Posições zeradas não aparecem. Migração direta do
computePositions do protótipo HTML.
"""

from decimal import Decimal

from core.entities import Posicao, TipoOperacao
from core.ports import RepositorioAtivos, RepositorioCotacoes, RepositorioOperacoes


class ConsolidarPosicoes:
    def __init__(
        self,
        repo_ativos: RepositorioAtivos,
        repo_operacoes: RepositorioOperacoes,
        repo_cotacoes: RepositorioCotacoes | None = None,
    ) -> None:
        self._repo_ativos = repo_ativos
        self._repo_operacoes = repo_operacoes
        self._repo_cotacoes = repo_cotacoes

    def executar(self) -> list[Posicao]:
        acumulado: dict[str, dict[str, Decimal]] = {}
        operacoes = sorted(self._repo_operacoes.listar_todas(), key=lambda o: o.data)

        for op in operacoes:
            p = acumulado.setdefault(op.ticker, {"qtd": Decimal("0"), "pm": Decimal("0")})
            if op.tipo == TipoOperacao.COMPRA:
                nova_qtd = p["qtd"] + op.quantidade
                p["pm"] = (p["pm"] * p["qtd"] + op.preco_unitario * op.quantidade) / nova_qtd
                p["qtd"] = nova_qtd
            else:
                p["qtd"] -= op.quantidade  # venda mantém o preço médio

        posicoes: list[Posicao] = []
        for ticker, p in acumulado.items():
            if p["qtd"] <= 0:
                continue
            ativo = self._repo_ativos.buscar_por_ticker(ticker)
            if ativo is None:
                continue
            cotacao = self._repo_cotacoes.cotacao_atual(ticker) if self._repo_cotacoes else None
            posicoes.append(
                Posicao(
                    ativo=ativo,
                    quantidade=p["qtd"],
                    preco_medio=p["pm"],
                    cotacao_atual=cotacao,
                )
            )

        posicoes.sort(
            key=lambda p: p.valor_mercado if p.valor_mercado is not None else p.custo_total,
            reverse=True,
        )
        return posicoes
