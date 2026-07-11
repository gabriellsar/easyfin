"""Caso de uso: consolidar operações em posições (equivale ao computePositions
do protótipo HTML) e marcar a mercado com as cotações atuais."""

from core.entities import Posicao
from core.ports import ProvedorCotacoes, RepositorioAtivos, RepositorioOperacoes


class ConsolidarPosicoes:
    def __init__(
        self,
        repo_ativos: RepositorioAtivos,
        repo_operacoes: RepositorioOperacoes,
        cotacoes: ProvedorCotacoes | None = None,
    ) -> None:
        self._repo_ativos = repo_ativos
        self._repo_operacoes = repo_operacoes
        self._cotacoes = cotacoes

    def executar(self) -> list[Posicao]:
        # TODO(passo 1): agrupar operações por ticker, calcular quantidade e
        # preço médio ponderado; se houver provedor de cotações, marcar a mercado.
        raise NotImplementedError
