"""Testes de integração dos endpoints (DRF APIClient + banco de teste)."""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from portfolio.models import Ativo, Cotacao


@pytest.fixture
def client_autenticado(db) -> APIClient:
    user = User.objects.create_user(username="teste", password="teste123")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def petr4(db) -> Ativo:
    ativo = Ativo.objects.create(ticker="PETR4", nome="Petrobras PN", classe=Ativo.Classe.ACAO)
    Cotacao.objects.create(
        ativo=ativo, preco=Decimal("41.87"), fechamento_anterior=Decimal("41.52")
    )
    return ativo


def _compra(ticker="PETR4", quantidade="100", preco="36.10"):
    return {
        "ticker": ticker,
        "tipo": "compra",
        "quantidade": quantidade,
        "preco_unitario": preco,
        "data": "2026-01-15",
    }


def test_endpoints_exigem_autenticacao(db):
    assert APIClient().get("/api/ativos/").status_code == 401


def test_listar_ativos(client_autenticado, petr4):
    resp = client_autenticado.get("/api/ativos/")
    assert resp.status_code == 200
    assert resp.data["results"][0]["ticker"] == "PETR4"
    assert resp.data["results"][0]["cotacao_atual"] is not None


def test_registrar_compra(client_autenticado, petr4):
    resp = client_autenticado.post("/api/operacoes/", _compra(), format="json")
    assert resp.status_code == 201
    assert resp.data["ticker"] == "PETR4"

    listagem = client_autenticado.get("/api/operacoes/")
    assert listagem.data["count"] == 1


def test_venda_sem_saldo_retorna_400(client_autenticado, petr4):
    client_autenticado.post("/api/operacoes/", _compra(quantidade="100"), format="json")
    resp = client_autenticado.post(
        "/api/operacoes/",
        {**_compra(quantidade="150", preco="42.30"), "tipo": "venda"},
        format="json",
    )
    assert resp.status_code == 400
    assert "indisponível" in resp.data["detail"]


def test_ticker_inexistente_retorna_400(client_autenticado, db):
    resp = client_autenticado.post("/api/operacoes/", _compra(ticker="XXXX4"), format="json")
    assert resp.status_code == 400


def test_listar_posicoes(client_autenticado, petr4):
    client_autenticado.post("/api/operacoes/", _compra(), format="json")
    resp = client_autenticado.get("/api/posicoes/")
    assert resp.status_code == 200
    posicao = resp.data[0]
    assert posicao["ticker"] == "PETR4"
    assert Decimal(posicao["valor_mercado"]) == Decimal("4187.00")
    assert Decimal(posicao["percentual_carteira"]) == Decimal("100.00")


def test_resumo_carteira(client_autenticado, petr4):
    client_autenticado.post("/api/operacoes/", _compra(), format="json")
    resp = client_autenticado.get("/api/carteira/resumo/")
    assert resp.status_code == 200
    assert Decimal(resp.data["patrimonio"]) == Decimal("4187.00")
    # (41.87 - 41.52) * 100
    assert Decimal(resp.data["resultado_dia"]) == Decimal("35.00")
    assert resp.data["quantidade_posicoes"] == 1


def test_rentabilidade_series_alinhadas(client_autenticado, db):
    resp = client_autenticado.get("/api/carteira/rentabilidade/?meses=12")
    assert resp.status_code == 200
    assert len(resp.data["datas"]) == len(resp.data["carteira"])
    assert len(resp.data["carteira"]) == len(resp.data["cdi"]) == len(resp.data["ibovespa"])


def test_rentabilidade_meses_invalido(client_autenticado, db):
    assert client_autenticado.get("/api/carteira/rentabilidade/?meses=abc").status_code == 400
    assert client_autenticado.get("/api/carteira/rentabilidade/?meses=0").status_code == 400


def test_atualizar_cotacoes(client_autenticado, petr4):
    resp = client_autenticado.post("/api/cotacoes/atualizar/")
    assert resp.status_code == 200
    assert resp.data["atualizados"] == 1


def test_relatorio_excel(client_autenticado, petr4):
    client_autenticado.post("/api/operacoes/", _compra(), format="json")
    resp = client_autenticado.get("/api/relatorios/excel/")
    assert resp.status_code == 200
    conteudo = b"".join(resp.streaming_content)
    assert conteudo[:2] == b"PK"  # assinatura zip do .xlsx


def _registro(username="novo_usuario", password="SenhaForte#2026", email="novo@example.com"):
    return {"username": username, "email": email, "password": password}


def test_registro_cria_usuario_e_devolve_tokens(db):
    resp = APIClient().post("/api/auth/registro/", _registro(), format="json")
    assert resp.status_code == 201
    assert resp.data["username"] == "novo_usuario"
    assert "access" in resp.data and "refresh" in resp.data
    assert User.objects.filter(username="novo_usuario").exists()

    # o token devolvido já autentica
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    assert client.get("/api/ativos/").status_code == 200


def test_registro_username_duplicado_retorna_400(db):
    User.objects.create_user(username="repetido", password="SenhaForte#2026")
    resp = APIClient().post("/api/auth/registro/", _registro(username="Repetido"), format="json")
    assert resp.status_code == 400
    assert "username" in resp.data


def test_registro_senha_fraca_retorna_400(db):
    resp = APIClient().post("/api/auth/registro/", _registro(password="123"), format="json")
    assert resp.status_code == 400
    assert "password" in resp.data


def test_registro_email_opcional(db):
    dados = {"username": "sem_email", "password": "SenhaForte#2026"}
    resp = APIClient().post("/api/auth/registro/", dados, format="json")
    assert resp.status_code == 201
