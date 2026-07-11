"""Caso de uso: registrar compra ou venda.

Regras:
- Ativo precisa existir (AtivoInexistenteError).
- Quantidade e preço devem ser maiores que zero.
- Venda: valida quantidade disponível em carteira (SaldoInsuficienteError).
O preço médio não é armazenado: é derivado das operações na consolidação.
"""

from decimal import Decimal

from core.entities import (
    AtivoInexistenteError,
    Operacao,
    SaldoInsuficienteError,
    TipoOperacao,
)
from core.ports import RepositorioAtivos, RepositorioOperacoes


class RegistrarOperacao:
    def __init__(
        self,
        repo_ativos: RepositorioAtivos,
        repo_operacoes: RepositorioOperacoes,
    ) -> None:
        self._repo_ativos = repo_ativos
        self._repo_operacoes = repo_operacoes

    def executar(self, operacao: Operacao) -> Operacao:
        if self._repo_ativos.buscar_por_ticker(operacao.ticker) is None:
            raise AtivoInexistenteError(f"Ativo {operacao.ticker} não cadastrado.")
        if operacao.quantidade <= 0:
            raise ValueError("Informe uma quantidade maior que zero.")
        if operacao.preco_unitario <= 0:
            raise ValueError("Informe um preço unitário maior que zero.")

        if operacao.tipo == TipoOperacao.VENDA:
            saldo = self._saldo_disponivel(operacao.ticker)
            if operacao.quantidade > saldo:
                raise SaldoInsuficienteError(
                    f"Quantidade indisponível: você possui {saldo.normalize():f} un. "
                    f"de {operacao.ticker}."
                )

        return self._repo_operacoes.salvar(operacao)

    def _saldo_disponivel(self, ticker: str) -> Decimal:
        saldo = Decimal("0")
        for op in self._repo_operacoes.listar_por_ticker(ticker):
            if op.tipo == TipoOperacao.COMPRA:
                saldo += op.quantidade
            else:
                saldo -= op.quantidade
        return saldo
