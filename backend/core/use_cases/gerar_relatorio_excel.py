"""Caso de uso: gerar relatório .xlsx com abas Posições e Operações."""

from core.ports import GeradorRelatorio, RepositorioOperacoes
from core.use_cases.consolidar_posicoes import ConsolidarPosicoes


class GerarRelatorioExcel:
    def __init__(
        self,
        consolidar_posicoes: ConsolidarPosicoes,
        repo_operacoes: RepositorioOperacoes,
        gerador: GeradorRelatorio,
    ) -> None:
        self._consolidar_posicoes = consolidar_posicoes
        self._repo_operacoes = repo_operacoes
        self._gerador = gerador

    def executar(self) -> bytes:
        posicoes = self._consolidar_posicoes.executar()
        operacoes = self._repo_operacoes.listar_todas()
        return self._gerador.gerar(posicoes, operacoes)
