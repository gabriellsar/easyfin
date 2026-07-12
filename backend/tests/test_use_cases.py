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
from core.use_cases.calcular_rentabilidade import CalcularRentabilidade
from core.use_cases.consolidar_posicoes import ConsolidarPosicoes
from core.use_cases.registrar_operacao import RegistrarOperacao


class RepositorioAtivosFake:
    def __init__(self, ativos: list[Ativo]) -> None:
        self._ativos = {a.ticker: a for a in ativos}

    def buscar_por_ticker(self, ticker: str) -> Ativo | None:
        return self._ativos.get(ticker)

    def listar(self) -> list[Ativo]:
        return list(self._ativos.values())

    def salvar(self, ativo: Ativo) -> Ativo:
        self._ativos[ativo.ticker] = ativo
        return ativo


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

    def salvar(
        self, ticker: str, preco: Decimal, fechamento_anterior: Decimal | None = None
    ) -> None:
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


class ProvedorFake:
    """Provedor sem série 'carteira' pronta — força o cálculo no domínio."""

    def __init__(
        self,
        precos: dict[str, dict[date, Decimal]] | None = None,
        ativos_conhecidos: dict[str, Ativo] | None = None,
    ) -> None:
        self._precos = precos or {}
        self._ativos_conhecidos = ativos_conhecidos or {}

    def cotacao_atual(self, ticker: str) -> Decimal | None:
        return None

    def fechamento_anterior(self, ticker: str) -> Decimal | None:
        return None

    def serie_indice(self, indice: str, inicio: date, fim: date) -> dict[date, Decimal]:
        return {}

    def serie_precos(self, ticker: str, inicio: date, fim: date) -> dict[date, Decimal]:
        return self._precos.get(ticker, {})

    def buscar_ativo(self, ticker: str) -> Ativo | None:
        return self._ativos_conhecidos.get(ticker)


class TestCalcularRentabilidade:
    HOJE = date(2026, 7, 15)  # janela de 3 meses: abr, mai, jun/2026

    def _executar(self, operacoes, precos):
        repo = RepositorioOperacoesFake()
        for op in operacoes:
            repo.salvar(op)
        uc = CalcularRentabilidade(repo, ProvedorFake(precos))
        return uc.executar(meses=3, hoje=self.HOJE)

    def test_carteira_calculada_por_dietz_mensal(self):
        # compra em abril; preço sobe 10% em maio e fica estável em junho
        op = Operacao(
            ticker="PETR4",
            tipo=TipoOperacao.COMPRA,
            quantidade=Decimal("100"),
            preco_unitario=Decimal("10"),
            data=date(2026, 4, 10),
        )
        precos = {
            "PETR4": {
                date(2026, 4, 1): Decimal("10"),
                date(2026, 5, 1): Decimal("11"),
                date(2026, 6, 1): Decimal("11"),
            }
        }
        serie = self._executar([op], precos)
        assert serie["datas"] == [date(2026, 4, 1), date(2026, 5, 1), date(2026, 6, 1)]
        assert serie["carteira"] == pytest.approx([0.0, 10.0, 10.0])

    def test_ticker_sem_historico_usa_preco_medio_e_nao_rende(self):
        op = Operacao(
            ticker="PETR4",
            tipo=TipoOperacao.COMPRA,
            quantidade=Decimal("10"),
            preco_unitario=Decimal("100"),
            data=date(2026, 4, 10),
        )
        serie = self._executar([op], precos={})
        assert serie["carteira"] == pytest.approx([0.0, 0.0, 0.0])

    def test_sem_operacoes_serie_zerada(self):
        serie = self._executar([], precos={})
        assert serie["carteira"] == pytest.approx([0.0, 0.0, 0.0])


class TestRegistrarOperacaoComAtivoNovo:
    """Ticker fora do banco: busca na fonte externa e cadastra automaticamente."""

    BBDC4 = Ativo(ticker="BBDC4", nome="Banco Bradesco PN", classe=ClasseAtivo.ACAO)

    def _uc(self, provedor):
        self.repo_ativos = RepositorioAtivosFake([PETR4])
        self.repo_ops = RepositorioOperacoesFake()
        return RegistrarOperacao(self.repo_ativos, self.repo_ops, provedor)

    def _compra_bbdc4(self):
        return Operacao(
            ticker="BBDC4",
            tipo=TipoOperacao.COMPRA,
            quantidade=Decimal("10"),
            preco_unitario=Decimal("15"),
            data=date(2026, 1, 15),
        )

    def test_ativo_novo_e_cadastrado_e_operacao_registrada(self):
        uc = self._uc(ProvedorFake(ativos_conhecidos={"BBDC4": self.BBDC4}))
        uc.executar(self._compra_bbdc4())
        assert self.repo_ativos.buscar_por_ticker("BBDC4") == self.BBDC4
        assert len(self.repo_ops.listar_todas()) == 1

    def test_ticker_desconhecido_da_fonte_levanta_erro(self):
        uc = self._uc(ProvedorFake())
        with pytest.raises(AtivoInexistenteError, match="não encontrado na B3"):
            uc.executar(self._compra_bbdc4())

    def test_sem_provedor_mantem_comportamento_antigo(self):
        uc = RegistrarOperacao(RepositorioAtivosFake([PETR4]), RepositorioOperacoesFake())
        with pytest.raises(AtivoInexistenteError):
            uc.executar(self._compra_bbdc4())
