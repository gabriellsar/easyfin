"""Views DRF — só orquestram: validam entrada, chamam o caso de uso e
serializam a saída. Nenhuma regra de negócio aqui."""

from decimal import Decimal
from io import BytesIO

from django.http import FileResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api import deps
from api.serializers import (
    AtivoSerializer,
    OperacaoCreateSerializer,
    OperacaoSerializer,
    PosicaoSerializer,
)
from core.entities import (
    AtivoInexistenteError,
    Operacao as OperacaoEntidade,
    SaldoInsuficienteError,
    TipoOperacao,
)
from portfolio.models import Ativo, Operacao


class AtivoListView(ListAPIView):
    queryset = Ativo.objects.select_related("cotacao").all()
    serializer_class = AtivoSerializer


class OperacaoListCreateView(ListAPIView):
    queryset = Operacao.objects.select_related("ativo").all()
    serializer_class = OperacaoSerializer

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
            criada = deps.registrar_operacao().executar(entidade)
        except (AtivoInexistenteError, SaldoInsuficienteError, ValueError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        posicoes = deps.consolidar_posicoes().executar()
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
        resumo = deps.resumo_carteira().executar()
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

        serie = deps.calcular_rentabilidade().executar(meses=meses)
        return Response(
            {
                "datas": [d.isoformat() for d in serie["datas"]],
                "carteira": serie["carteira"],
                "cdi": serie["cdi"],
                "ibovespa": serie["ibovespa"],
            }
        )


class CotacoesAtualizarView(APIView):
    def post(self, request):
        atualizados = deps.atualizar_cotacoes().executar()
        return Response({"atualizados": atualizados})


class RelatorioExcelView(APIView):
    def get(self, request):
        conteudo = deps.gerar_relatorio_excel().executar()
        return FileResponse(
            BytesIO(conteudo),
            as_attachment=True,
            filename="EasyFin_relatorio.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
