"""Caso de uso: buscar cotações no provedor externo e remarcar a mercado,
persistindo a última cotação conhecida (e o fechamento anterior) de cada
ativo. Tickers que a fonte não conhece (ex.: títulos do Tesouro) mantêm a
última cotação armazenada."""

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
            if preco is None:
                continue
            anterior = self._provedor.fechamento_anterior(ativo.ticker)
            self._repo_cotacoes.salvar(ativo.ticker, preco, anterior)
            atualizados += 1
        return atualizados
