from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from portfolio.models import Ativo, Operacao


class RegistroSerializer(serializers.Serializer):
    """Entrada do POST /api/auth/registro/ — criação de conta."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_username(self, valor: str) -> str:
        if User.objects.filter(username__iexact=valor).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return valor

    def validate_password(self, valor: str) -> str:
        try:
            validate_password(valor)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return valor

    def create(self, validated_data: dict) -> User:
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class AtivoSerializer(serializers.ModelSerializer):
    cotacao_atual = serializers.SerializerMethodField()

    class Meta:
        model = Ativo
        fields = ["id", "ticker", "nome", "classe", "cotacao_atual"]

    def get_cotacao_atual(self, obj) -> str | None:
        return str(obj.cotacao.preco) if hasattr(obj, "cotacao") else None


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
