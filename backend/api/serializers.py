from rest_framework import serializers

from portfolio.models import Ativo, Operacao


class AtivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ativo
        fields = ["id", "ticker", "nome", "classe"]


class OperacaoSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source="ativo.ticker", read_only=True)

    class Meta:
        model = Operacao
        fields = ["id", "ticker", "tipo", "quantidade", "preco_unitario", "data"]


class OperacaoCreateSerializer(serializers.Serializer):
    """Entrada do POST /api/operacoes/ — a view repassa ao caso de uso
    RegistrarOperacao, que valida saldo e recalcula o PM."""

    ticker = serializers.CharField(max_length=12)
    tipo = serializers.ChoiceField(choices=Operacao.Tipo.choices)
    quantidade = serializers.DecimalField(max_digits=18, decimal_places=6, min_value=0)
    preco_unitario = serializers.DecimalField(max_digits=18, decimal_places=6, min_value=0)
    data = serializers.DateField()


class PosicaoSerializer(serializers.Serializer):
    """Saída de GET /api/posicoes/ — espelha core.entities.Posicao."""

    ticker = serializers.CharField()
    nome = serializers.CharField()
    classe = serializers.CharField()
    quantidade = serializers.DecimalField(max_digits=18, decimal_places=6)
    preco_medio = serializers.DecimalField(max_digits=18, decimal_places=6)
    cotacao_atual = serializers.DecimalField(max_digits=18, decimal_places=6, allow_null=True)
    custo = serializers.DecimalField(max_digits=18, decimal_places=2)
    valor_mercado = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    resultado = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    resultado_pct = serializers.DecimalField(max_digits=9, decimal_places=2, allow_null=True)
    percentual_carteira = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
