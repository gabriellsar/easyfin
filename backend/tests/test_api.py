"""Testes de integração dos endpoints (DRF APIClient + banco de teste)."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def client_autenticado(db) -> APIClient:
    user = User.objects.create_user(username="teste", password="teste123")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_endpoints_exigem_autenticacao(db):
    client = APIClient()
    resp = client.get("/api/ativos/")
    assert resp.status_code == 401


def test_listar_ativos_vazio(client_autenticado):
    resp = client_autenticado.get("/api/ativos/")
    assert resp.status_code == 200


@pytest.mark.skip(reason="TODO(passo 3): implementar POST /api/operacoes/")
def test_registrar_compra(client_autenticado): ...


@pytest.mark.skip(reason="TODO(passo 3): implementar GET /api/posicoes/")
def test_listar_posicoes(client_autenticado): ...
