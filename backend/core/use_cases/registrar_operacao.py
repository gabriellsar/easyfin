"""Caso de uso: registrar compra ou venda.

Regras:
- Quantidade e preço devem ser maiores que zero.
- Ativo desconhecido: se houver provedor de cotações, o ativo é buscado na
  fonte externa e cadastrado automaticamente (com a cotação inicial);
  se a fonte também não o conhece, AtivoInexistenteError.
- Venda: o histórico é revalidado com a operação inserida na sua data —
  o saldo do ticker não pode ficar negativo em nenhum ponto da linha do
  tempo (SaldoInsuficienteError), o que cobre também vendas retroativas
  que descobririam vendas já registradas.
O preço médio não é armazenado: é derivado das operações na consolidação.
"""

from decimal import Decimal

from core.entities import (
    AtivoInexistenteError,
    Operacao,
    SaldoInsuficienteError,
    TipoOperacao,
)
from core.ports import (
    ProvedorCotacoes,
    RepositorioAtivos,
    RepositorioCotacoes,
    RepositorioOperacoes,
)


class RegistrarOperacao:
    def __init__(
        self,
        repo_ativos: RepositorioAtivos,
        repo_operacoes: RepositorioOperacoes,
        provedor: ProvedorCotacoes | None = None,
        repo_cotacoes: RepositorioCotacoes | None = None,
    ) -> None:
        self._repo_ativos = repo_ativos
        self._repo_operacoes = repo_operacoes
        self._provedor = provedor
        self._repo_cotacoes = repo_cotacoes

    def executar(self, operacao: Operacao) -> Operacao:
        if operacao.quantidade <= 0:
            raise ValueError("Informe uma quantidade maior que zero.")
        if operacao.preco_unitario <= 0:
            raise ValueError("Informe um preço unitário maior que zero.")

        if self._repo_ativos.buscar_por_ticker(operacao.ticker) is None:
            self._cadastrar_ativo_externo(operacao.ticker)

        if operacao.tipo == TipoOperacao.VENDA:
            self._validar_saldo_na_linha_do_tempo(operacao)

        return self._repo_operacoes.salvar(operacao)

    def _cadastrar_ativo_externo(self, ticker: str) -> None:
        ativo = self._provedor.buscar_ativo(ticker) if self._provedor else None
        if ativo is None:
            raise AtivoInexistenteError(
                f"Ativo {ticker} não encontrado na B3. Confira o ticker."
            )
        self._repo_ativos.salvar(ativo)

        # marca a mercado desde já, se a fonte tiver a cotação
        if self._repo_cotacoes is not None:
            preco = self._provedor.cotacao_atual(ticker)
            if preco is not None:
                self._repo_cotacoes.salvar(
                    ticker, preco, self._provedor.fechamento_anterior(ticker)
                )

    def _validar_saldo_na_linha_do_tempo(self, venda: Operacao) -> None:
        # No mesmo dia, compras contam antes das vendas (permite comprar e
        # vender na mesma data).
        operacoes = [*self._repo_operacoes.listar_por_ticker(venda.ticker), venda]
        operacoes.sort(key=lambda o: (o.data, o.tipo != TipoOperacao.COMPRA))

        saldo = Decimal("0")
        for op in operacoes:
            if op.tipo == TipoOperacao.COMPRA:
                saldo += op.quantidade
                continue
            saldo -= op.quantidade
            if saldo >= 0:
                continue
            if op is venda:
                disponivel = saldo + venda.quantidade
                raise SaldoInsuficienteError(
                    f"Quantidade indisponível: você possui {disponivel.normalize():f} un. "
                    f"de {venda.ticker} em {venda.data:%d/%m/%Y}."
                )
            raise SaldoInsuficienteError(
                f"Esta venda deixaria o saldo de {venda.ticker} negativo em "
                f"{op.data:%d/%m/%Y}, data de uma venda já registrada."
            )
