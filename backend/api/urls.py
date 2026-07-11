from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api import views

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("ativos/", views.AtivoListView.as_view(), name="ativos"),
    path("operacoes/", views.OperacaoListCreateView.as_view(), name="operacoes"),
    path("posicoes/", views.PosicaoListView.as_view(), name="posicoes"),
    path("carteira/resumo/", views.CarteiraResumoView.as_view(), name="carteira_resumo"),
    path(
        "carteira/rentabilidade/",
        views.CarteiraRentabilidadeView.as_view(),
        name="carteira_rentabilidade",
    ),
    path("cotacoes/atualizar/", views.CotacoesAtualizarView.as_view(), name="cotacoes_atualizar"),
    path("relatorios/excel/", views.RelatorioExcelView.as_view(), name="relatorio_excel"),
]
