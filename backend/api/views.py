"""Views DRF — só orquestram: validam entrada, chamam o caso de uso e
serializam a saída. Nenhuma regra de negócio aqui."""

from decimal import Decimal
from io import BytesIO

from django.http import FileResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from api import deps
from api.serializers import (
    AtivoSerializer,
    OperacaoCreateSerializer,
    OperacaoSerializer,
    PosicaoSerializer,
    RegistroSerializer,
)
from core.use_cases.calcular_rentabilidade import INDICES_SUPORTADOS
from core.entities import (
    AtivoInexistenteError,
    FonteExternaError,
    Operacao as OperacaoEntidade,
    SaldoInsuficienteError,
    TipoOperacao,
)
from portfolio.models import Ativo, Operacao

RESPOSTA_FONTE_INDISPONIVEL = {
    "detail": "Fonte externa de cotações indisponível no momento. Tente novamente."
}


class RegistroView(APIView):
    """Criação de conta — público. Devolve o par JWT para login imediato."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        tokens = RefreshToken.for_user(usuario)
        return Response(
            {
                "username": usuario.username,
                "access": str(tokens.access_token),
                "refresh": str(tokens),
            },
            status=status.HTTP_201_CREATED,
        )


class AtivoListView(ListAPIView):
    queryset = Ativo.objects.select_related("cotacao").all()
    serializer_class = AtivoSerializer


class OperacaoListCreateView(ListAPIView):
    serializer_class = OperacaoSerializer

    def get_queryset(self):
        return Operacao.objects.select_related("ativo").filter(usuario=self.request.user)

    def post(self, request):
        entrada = OperacaoCreateSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        dados = entrada.validated_data

        entidade = OperacaoEntidade(
            ticker=dados["ticker"].upper(),
            tipo=TipoOperacao(dados["tipo"]),
            quantidade=dados["quantidade"],
            preco_unitario=dados["preco_unitario"],
            data=dados["data"],
        )
        try:
            criada = deps.registrar_operacao(request.user).executar(entidade)
        except (AtivoInexistenteError, SaldoInsuficienteError, ValueError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except FonteExternaError:
            return Response(
                RESPOSTA_FONTE_INDISPONIVEL, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response(
            {
                "id": criada.id,
                "ticker": criada.ticker,
                "tipo": criada.tipo.value,
                "quantidade": str(criada.quantidade),
                "preco_unitario": str(criada.preco_unitario),
                "data": criada.data.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class PosicaoListView(APIView):
    def get(self, request):
        posicoes = deps.consolidar_posicoes(request.user).executar()
        total = sum((p.valor_mercado for p in posicoes if p.valor_mercado), Decimal("0"))
        itens = [
            {
                "ticker": p.ativo.ticker,
                "nome": p.ativo.nome,
                "classe": p.ativo.classe.value,
                "quantidade": p.quantidade,
                "preco_medio": p.preco_medio,
                "cotacao_atual": p.cotacao_atual,
                "custo": p.custo_total,
                "valor_mercado": p.valor_mercado,
                "resultado": p.resultado,
                "resultado_pct": p.resultado_pct,
                "percentual_carteira": (
                    p.valor_mercado / total * 100 if p.valor_mercado and total else None
                ),
            }
            for p in posicoes
        ]
        return Response(PosicaoSerializer(itens, many=True).data)


class CarteiraResumoView(APIView):
    def get(self, request):
        try:
            resumo = deps.resumo_carteira(request.user).executar()
        except FonteExternaError:
            return Response(
                RESPOSTA_FONTE_INDISPONIVEL, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response(
            {
                "patrimonio": str(resumo["patrimonio"].quantize(Decimal("0.01"))),
                "resultado_dia": str(resumo["resultado_dia"].quantize(Decimal("0.01"))),
                "resultado_dia_pct": str(resumo["resultado_dia_pct"].quantize(Decimal("0.01"))),
                "rentabilidade_12m": str(round(resumo["rentabilidade_12m"], 2)),
                "percentual_cdi": str(round(resumo["percentual_cdi"], 1)),
                "quantidade_posicoes": resumo["quantidade_posicoes"],
                "quantidade_classes": resumo["quantidade_classes"],
            }
        )


class CarteiraRentabilidadeView(APIView):
    def get(self, request):
        try:
            meses = int(request.query_params.get("meses", 12))
        except ValueError:
            return Response(
                {"detail": "Parâmetro 'meses' deve ser um inteiro."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not 1 <= meses <= 120:
            return Response(
                {"detail": "Parâmetro 'meses' deve estar entre 1 e 120."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        brutos = request.query_params.get("indices", "cdi,ibovespa")
        indices = [i.strip().lower() for i in brutos.split(",") if i.strip()]
        invalidos = sorted(set(indices) - set(INDICES_SUPORTADOS))
        if invalidos:
            return Response(
                {
                    "detail": (
                        f"Índices inválidos: {', '.join(invalidos)}. "
                        f"Disponíveis: {', '.join(INDICES_SUPORTADOS)}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serie = deps.calcular_rentabilidade(request.user).executar(
                meses=meses, indices=indices
            )
        except FonteExternaError:
            return Response(
                RESPOSTA_FONTE_INDISPONIVEL, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response(
            {
                "datas": [d.isoformat() for d in serie["datas"]],
                "carteira": serie["carteira"],
                "indices": serie["indices"],
            }
        )


class CotacoesAtualizarView(APIView):
    def post(self, request):
        try:
            atualizados = deps.atualizar_cotacoes().executar()
        except FonteExternaError:
            return Response(
                RESPOSTA_FONTE_INDISPONIVEL, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response({"atualizados": atualizados})


class RelatorioExcelView(APIView):
    def get(self, request):
        conteudo = deps.gerar_relatorio_excel(request.user).executar()
        return FileResponse(
            BytesIO(conteudo),
            as_attachment=True,
            filename="EasyFin_relatorio.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
