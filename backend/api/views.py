"""Views DRF — só orquestram: validam entrada, chamam o caso de uso e
serializam a saída. Nenhuma regra de negócio aqui."""

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import AtivoSerializer, OperacaoSerializer
from portfolio.models import Ativo, Operacao


class AtivoListView(ListAPIView):
    queryset = Ativo.objects.all()
    serializer_class = AtivoSerializer


class OperacaoListCreateView(APIView):
    def get(self, request):
        qs = Operacao.objects.select_related("ativo").all()
        return Response(OperacaoSerializer(qs, many=True).data)

    def post(self, request):
        # TODO(passo 3): validar com OperacaoCreateSerializer e chamar
        # RegistrarOperacao; mapear SaldoInsuficienteError -> 400.
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class PosicaoListView(APIView):
    def get(self, request):
        # TODO(passo 3): chamar ConsolidarPosicoes e serializar com PosicaoSerializer.
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class CarteiraResumoView(APIView):
    def get(self, request):
        # TODO(passo 4): KPIs — patrimônio, resultado do dia, rentabilidade 12m, % do CDI.
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class CarteiraRentabilidadeView(APIView):
    def get(self, request):
        # TODO(passo 4): CalcularRentabilidade(meses=request.query_params["meses"]).
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class CotacoesAtualizarView(APIView):
    def post(self, request):
        # TODO(passo 4): buscar cotações (brapi + BCB) e remarcar a mercado.
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class RelatorioExcelView(APIView):
    def get(self, request):
        # TODO(passo 5): GerarRelatorioExcel -> FileResponse com o .xlsx.
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
