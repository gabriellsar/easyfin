"""Testes unitários dos casos de uso — sem banco, com repositórios fake."""

from datetime import date
from decimal import Decimal

import pytest

from core.entities import (
    Ativo,
    AtivoInexistenteError,
    ClasseAtivo,
    Operacao,
    SaldoInsuficienteError,
    TipoOperacao,
)
from core.use_cases.consolidar_posicoes import ConsolidarPosicoes
from core.use_cases.registrar_operacao import RegistrarOperacao


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


class RepositorioCotacoesFake:
    def __init__(self, cotacoes: dict[str, Decimal] | None = None) -> None:
        self._cotacoes = cotacoes or {}

    def cotacao_atual(self, ticker: str) -> Decimal | None:
        return self._cotacoes.get(ticker)

    def fechamento_anterior(self, ticker: str) -> Decimal | None:
        return None

    def salvar(self, ticker: str, preco: Decimal) -> None:
        self._cotacoes[ticker] = preco


PETR4 = Ativo(ticker="PETR4", nome="Petrobras PN", classe=ClasseAtivo.ACAO)


def _op(tipo: TipoOperacao, qtd: str, preco: str, dia: int = 1) -> Operacao:
    return Operacao(
        ticker="PETR4",
        tipo=tipo,
        quantidade=Decimal(qtd),
        preco_unitario=Decimal(preco),
        data=date(2026, 1, dia),
    )


def _compra(qtd: str, preco: str, dia: int = 1) -> Operacao:
    return _op(TipoOperacao.COMPRA, qtd, preco, dia)


def _venda(qtd: str, preco: str, dia: int = 2) -> Operacao:
    return _op(TipoOperacao.VENDA, qtd, preco, dia)


class TestRegistrarOperacao:
    def setup_method(self):
        self.repo_ops = RepositorioOperacoesFake()
        self.uc = RegistrarOperacao(RepositorioAtivosFake([PETR4]), self.repo_ops)

    def test_compra_valida_e_persistida(self):
        criada = self.uc.executar(_compra("100", "36.10"))
        assert criada.quantidade == Decimal("100")
        assert len(self.repo_ops.listar_todas()) == 1

    def test_venda_com_saldo_e_aceita(self):
        self.uc.executar(_compra("100", "36.10"))
        self.uc.executar(_venda("40", "42.30"))
        assert len(self.repo_ops.listar_todas()) == 2

    def test_venda_sem_saldo_levanta_erro(self):
        self.uc.executar(_compra("100", "36.10"))
        with pytest.raises(SaldoInsuficienteError, match="100"):
            self.uc.executar(_venda("150", "42.30"))

    def test_ticker_inexistente_levanta_erro(self):
        op = Operacao(
            ticker="XXXX4",
            tipo=TipoOperacao.COMPRA,
            quantidade=Decimal("10"),
            preco_unitario=Decimal("10"),
            data=date(2026, 1, 1),
        )
        with pytest.raises(AtivoInexistenteError):
            self.uc.executar(op)

    def test_quantidade_zero_levanta_erro(self):
        with pytest.raises(ValueError, match="quantidade"):
            self.uc.executar(_compra("0", "36.10"))

    def test_preco_zero_levanta_erro(self):
        with pytest.raises(ValueError, match="preço"):
            self.uc.executar(_compra("10", "0"))


class TestConsolidarPosicoes:
    def _consolidar(self, operacoes: list[Operacao], cotacoes=None):
        repo_ops = RepositorioOperacoesFake()
        for op in operacoes:
            repo_ops.salvar(op)
        uc = ConsolidarPosicoes(
            RepositorioAtivosFake([PETR4]),
            repo_ops,
            RepositorioCotacoesFake(cotacoes) if cotacoes else None,
        )
        return uc.executar()

    def test_preco_medio_ponderado_em_compras_sucessivas(self):
        # (200*36.10 + 100*38.65) / 300 = 36.95
        posicoes = self._consolidar([_compra("200", "36.10", 1), _compra("100", "38.65", 5)])
        assert len(posicoes) == 1
        assert posicoes[0].quantidade == Decimal("300")
        assert posicoes[0].preco_medio == Decimal("36.95")

    def test_venda_reduz_quantidade_sem_alterar_pm(self):
        posicoes = self._consolidar(
            [_compra("200", "36.10", 1), _compra("100", "38.65", 5), _venda("50", "42.30", 10)]
        )
        assert posicoes[0].quantidade == Decimal("250")
        assert posicoes[0].preco_medio == Decimal("36.95")

    def test_posicao_zerada_nao_aparece(self):
        posicoes = self._consolidar([_compra("10", "36.10", 1), _venda("10", "42.30", 5)])
        assert posicoes == []

    def test_marcacao_a_mercado_com_cotacao(self):
        posicoes = self._consolidar(
            [_compra("100", "36.10")], cotacoes={"PETR4": Decimal("41.87")}
        )
        p = posicoes[0]
        assert p.valor_mercado == Decimal("4187.00")
        assert p.resultado == Decimal("577.00")

    def test_sem_repositorio_de_cotacoes_valor_mercado_e_nulo(self):
        posicoes = self._consolidar([_compra("100", "36.10")])
        assert posicoes[0].valor_mercado is None
        assert posicoes[0].resultado_pct is None
