"""Gerador de relatório Excel (openpyxl) — implementa o port GeradorRelatorio."""

from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook

from core.entities import Operacao, Posicao


class OpenpyxlWriter:
    def gerar(self, posicoes: list[Posicao], operacoes: list[Operacao]) -> bytes:
        wb = Workbook()

        aba_pos = wb.active
        aba_pos.title = "Posições"
        aba_pos.append([
            "Ativo", "Nome", "Classe", "Quantidade", "Preço médio (R$)",
            "Cotação (R$)", "Custo (R$)", "Valor de mercado (R$)",
            "Resultado (R$)", "Resultado (%)", "% carteira",
        ])
        total = sum((p.valor_mercado for p in posicoes if p.valor_mercado), Decimal("0"))
        for p in posicoes:
            pct_carteira = (
                float(p.valor_mercado / total * 100) if p.valor_mercado and total else None
            )
            aba_pos.append([
                p.ativo.ticker,
                p.ativo.nome,
                p.ativo.classe.value,
                float(p.quantidade),
                round(float(p.preco_medio), 2),
                float(p.cotacao_atual) if p.cotacao_atual is not None else None,
                round(float(p.custo_total), 2),
                round(float(p.valor_mercado), 2) if p.valor_mercado is not None else None,
                round(float(p.resultado), 2) if p.resultado is not None else None,
                round(float(p.resultado_pct), 2) if p.resultado_pct is not None else None,
                round(pct_carteira, 2) if pct_carteira is not None else None,
            ])

        aba_ops = wb.create_sheet("Operações")
        aba_ops.append(["Data", "Tipo", "Ativo", "Quantidade", "Preço (R$)", "Total (R$)"])
        for op in operacoes:
            aba_ops.append([
                op.data.isoformat(),
                "Compra" if op.tipo.value == "compra" else "Venda",
                op.ticker,
                float(op.quantidade),
                float(op.preco_unitario),
                round(float(op.valor_total), 2),
            ])

        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()
