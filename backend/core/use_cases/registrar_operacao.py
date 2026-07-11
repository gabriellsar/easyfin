"""Caso de uso: registrar compra ou venda.

Regras:
- Compra: recalcula o preço médio ponderado da posição.
- Venda: valida quantidade disponível (SaldoInsuficienteError) e mantém o PM.
"""

from core.entities import Operacao, TipoOperacao
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
        # TODO(passo 1): validar ativo existente, validar saldo em venda,
        # persistir via repositório. Migrar lógica do protótipo HTML.
        raise NotImplementedError
