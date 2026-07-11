"""Caso de uso: buscar cotações no provedor externo e remarcar a mercado,
persistindo a última cotação conhecida de cada ativo."""

from core.ports import ProvedorCotacoes, RepositorioAtivos, RepositorioCotacoes


class AtualizarCotacoes:
    def __init__(
        self,
        repo_ativos: RepositorioAtivos,
        provedor: ProvedorCotacoes,
        repo_cotacoes: RepositorioCotacoes,
    ) -> None:
        self._repo_ativos = repo_ativos
        self._provedor = provedor
        self._repo_cotacoes = repo_cotacoes

    def executar(self) -> int:
        atualizados = 0
        for ativo in self._repo_ativos.listar():
            preco = self._provedor.cotacao_atual(ativo.ticker)
            self._repo_cotacoes.salvar(ativo.ticker, preco)
            atualizados += 1
        return atualizados
