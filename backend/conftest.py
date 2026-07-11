"""Configuração global do pytest: testes usam o provedor de cotações mock
para não depender de rede (brapi/BCB)."""

import os

os.environ["MARKET_DATA_PROVIDER"] = "mock"
