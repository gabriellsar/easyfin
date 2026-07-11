"""Testes unitários dos casos de uso — sem banco, com repositórios fake.

Passo 1 da ordem de construção: escrever estes testes ANTES de implementar
registrar_operacao e consolidar_posicoes.
"""

from datetime import date
from decimal import Decimal

import pytest

from core.entities import Ativo, ClasseAtivo, Operacao, TipoOperacao


class RepositorioAtivosFake:
    def __init__(self, ativos: list[Ativo]) -> None:
        self._ativos = {a.ticker: a for a in ativos}

    def buscar_por_ticker(self, ticker: str) -> Ativo | None:
        return self._ativos.get(ticker)

    def listar(self) -> list[Ativo]:
        return list(self._ativos.values())


class RepositorioOperacoesFake:
    def __init__(self) -> None:
        self._operacoes: list[Operacao] = []

    def salvar(self, operacao: Operacao) -> Operacao:
        self._operacoes.append(operacao)
        return operacao

    def listar_por_ticker(self, ticker: str) -> list[Operacao]:
        return [o for o in self._operacoes if o.ticker == ticker]

    def listar_todas(self) -> list[Operacao]:
        return list(self._operacoes)


@pytest.fixture
def petr4() -> Ativo:
    return Ativo(ticker="PETR4", nome="Petrobras PN", classe=ClasseAtivo.ACAO)


def _compra(qtd: str, preco: str) -> Operacao:
    return Operacao(
        ticker="PETR4",
        tipo=TipoOperacao.COMPRA,
        quantidade=Decimal(qtd),
        preco_unitario=Decimal(preco),
        data=date(2026, 1, 15),
    )


@pytest.mark.skip(reason="TODO(passo 1): implementar RegistrarOperacao")
class TestRegistrarOperacao:
    def test_compra_valida_e_persistida(self, petr4): ...

    def test_venda_sem_saldo_levanta_erro(self, petr4): ...

    def test_ticker_inexistente_levanta_erro(self): ...


@pytest.mark.skip(reason="TODO(passo 1): implementar ConsolidarPosicoes")
class TestConsolidarPosicoes:
    def test_preco_medio_ponderado_em_compras_sucessivas(self, petr4): ...

    def test_venda_reduz_quantidade_sem_alterar_pm(self, petr4): ...

    def test_posicao_zerada_nao_aparece(self, petr4): ...
