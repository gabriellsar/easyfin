from django.db import models


class Ativo(models.Model):
    class Classe(models.TextChoices):
        ACAO = "acao", "Ação"
        FII = "fii", "FII"
        RENDA_FIXA = "renda_fixa", "Renda Fixa"
        ETF = "etf", "ETF"

    ticker = models.CharField(max_length=12, unique=True)
    nome = models.CharField(max_length=120)
    classe = models.CharField(max_length=12, choices=Classe.choices)

    class Meta:
        ordering = ["ticker"]

    def __str__(self) -> str:
        return self.ticker


class Operacao(models.Model):
    class Tipo(models.TextChoices):
        COMPRA = "compra", "Compra"
        VENDA = "venda", "Venda"

    ativo = models.ForeignKey(Ativo, on_delete=models.PROTECT, related_name="operacoes")
    tipo = models.CharField(max_length=6, choices=Tipo.choices)
    quantidade = models.DecimalField(max_digits=18, decimal_places=6)
    preco_unitario = models.DecimalField(max_digits=18, decimal_places=6)
    data = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data", "-criado_em"]

    def __str__(self) -> str:
        return f"{self.tipo} {self.quantidade} {self.ativo.ticker} @ {self.preco_unitario}"


class Cotacao(models.Model):
    """Última cotação conhecida de um ativo (atualizada via brapi/BCB)."""

    ativo = models.OneToOneField(Ativo, on_delete=models.CASCADE, related_name="cotacao")
    preco = models.DecimalField(max_digits=18, decimal_places=6)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.ativo.ticker}: {self.preco}"
