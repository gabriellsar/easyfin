"""Popula o banco com os dados de demonstração do protótipo easyfin-ui.html:
ativos, operações e cotações (com fechamento anterior). Idempotente."""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from infrastructure.mock_market_data import COTACOES_BASE, FECHAMENTO_ANTERIOR
from portfolio.models import Ativo, Cotacao, Operacao

ATIVOS = [
    ("PETR4", "Petrobras PN", Ativo.Classe.ACAO),
    ("VALE3", "Vale ON", Ativo.Classe.ACAO),
    ("ITUB4", "Itaú Unibanco PN", Ativo.Classe.ACAO),
    ("WEGE3", "WEG ON", Ativo.Classe.ACAO),
    ("BBAS3", "Banco do Brasil ON", Ativo.Classe.ACAO),
    ("KNRI11", "Kinea Renda Imob.", Ativo.Classe.FII),
    ("MXRF11", "Maxi Renda", Ativo.Classe.FII),
    ("TSELIC29", "Tesouro Selic 2029", Ativo.Classe.RENDA_FIXA),
]

OPERACOES = [
    (date(2025, 8, 5), Operacao.Tipo.COMPRA, "PETR4", "200", "36.10"),
    (date(2025, 8, 5), Operacao.Tipo.COMPRA, "ITUB4", "150", "33.40"),
    (date(2025, 9, 12), Operacao.Tipo.COMPRA, "VALE3", "100", "59.80"),
    (date(2025, 10, 3), Operacao.Tipo.COMPRA, "WEGE3", "120", "38.95"),
    (date(2025, 10, 20), Operacao.Tipo.COMPRA, "KNRI11", "40", "158.30"),
    (date(2025, 11, 14), Operacao.Tipo.COMPRA, "MXRF11", "500", "10.15"),
    (date(2025, 12, 2), Operacao.Tipo.COMPRA, "TSELIC29", "1", "15102.55"),
    (date(2026, 1, 15), Operacao.Tipo.COMPRA, "PETR4", "100", "38.65"),
    (date(2026, 2, 20), Operacao.Tipo.VENDA, "VALE3", "30", "65.10"),
    (date(2026, 3, 18), Operacao.Tipo.COMPRA, "BBAS3", "250", "27.40"),
    (date(2026, 5, 6), Operacao.Tipo.COMPRA, "ITUB4", "100", "36.20"),
    (date(2026, 6, 24), Operacao.Tipo.VENDA, "PETR4", "50", "42.30"),
]


class Command(BaseCommand):
    help = "Cria ativos, operações e cotações de demonstração (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--usuario",
            help="Username dono das operações demo (padrão: primeiro superusuário).",
        )

    def handle(self, *args, **options):
        from django.contrib.auth.models import User

        if options["usuario"]:
            usuario = User.objects.filter(username=options["usuario"]).first()
        else:
            usuario = User.objects.filter(is_superuser=True).order_by("pk").first()
        if usuario is None:
            self.stderr.write(
                "Nenhum usuário encontrado. Crie um (createsuperuser ou /api/auth/registro/) "
                "ou informe --usuario <username>."
            )
            return

        ativos = {}
        for ticker, nome, classe in ATIVOS:
            ativos[ticker], _ = Ativo.objects.get_or_create(
                ticker=ticker, defaults={"nome": nome, "classe": classe}
            )

        if Operacao.objects.filter(usuario=usuario).exists():
            self.stdout.write(f"{usuario.username} já tem operações — seed ignorado.")
        else:
            for data, tipo, ticker, qtd, preco in OPERACOES:
                Operacao.objects.create(
                    usuario=usuario,
                    ativo=ativos[ticker],
                    tipo=tipo,
                    quantidade=Decimal(qtd),
                    preco_unitario=Decimal(preco),
                    data=data,
                )
            self.stdout.write(f"{len(OPERACOES)} operações criadas para {usuario.username}.")

        for ticker, ativo in ativos.items():
            Cotacao.objects.update_or_create(
                ativo=ativo,
                defaults={
                    "preco": COTACOES_BASE[ticker],
                    "fechamento_anterior": FECHAMENTO_ANTERIOR[ticker],
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Seed concluído: {len(ativos)} ativos com cotações."))
