"""Gerador de relatório Excel (openpyxl) — implementa o port GeradorRelatorio."""

from core.entities import Operacao, Posicao


class OpenpyxlWriter:
    def gerar(self, posicoes: list[Posicao], operacoes: list[Operacao]) -> bytes:
        # TODO(passo 5): criar workbook com abas "Posições" e "Operações"
        # e retornar os bytes do .xlsx (BytesIO).
        raise NotImplementedError
