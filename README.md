# EasyFin

**Gestão de carteira de investimentos** — cadastro de ativos, registro de operações de compra e venda, cálculo de preço médio e posição consolidada, marcação a mercado com cotações reais e comparação de rentabilidade contra CDI e Ibovespa.

Projeto desenvolvido em equipe na PUC-Rio, evoluído a partir de um administrador financeiro genérico para um gestor de carteira com foco em renda variável.

```
API REST (Django REST Framework + PostgreSQL)  ·  SPA (Svelte 5 + Vite)
```

---

## Sumário

- [Visão geral](#visão-geral)
- [Por que Clean Architecture](#por-que-clean-architecture)
- [Anatomia do backend](#anatomia-do-backend)
- [O fluxo de uma requisição](#o-fluxo-de-uma-requisição)
- [Modelo de domínio](#modelo-de-domínio)
- [Fontes de dados de mercado](#fontes-de-dados-de-mercado)
- [Frontend](#frontend)
- [Testes](#testes)
- [Rodando localmente](#rodando-localmente)
- [Deploy](#deploy)
- [Decisões e trade-offs](#decisões-e-trade-offs)

---

## Visão geral

O EasyFin resolve um problema simples de enunciar e traiçoeiro de implementar corretamente: **dado um histórico de compras e vendas de um investidor, qual é a posição atual da carteira, quanto ela vale, e como seu desempenho se compara ao mercado?**

A resposta exige, ao mesmo tempo, regras de negócio nada triviais (preço médio ponderado, marcação a mercado, cálculo de rentabilidade por método de Dietz) e integração com múltiplas fontes de dados externas instáveis (brapi, Banco Central, Yahoo Finance). Foi essa combinação — **lógica de domínio densa** + **dependências externas voláteis** — que motivou a escolha arquitetural do projeto.

## Por que Clean Architecture

A versão original do projeto era um administrador financeiro comum: models Django com regras de negócio dentro de métodos e views, e chamadas HTTP a APIs externas feitas diretamente onde eram necessárias. Funcionava, mas tinha dois problemas que se agravariam à medida que o escopo crescesse de "administrador financeiro" para "gestor de carteira com marcação a mercado":

1. **Testar preço médio, posição consolidada e rentabilidade exigia banco de dados e rede.** Não dava para validar a fórmula de Dietz modificado sem subir Postgres e sem que a brapi respondesse.
2. **Trocar de fonte de cotação (brapi → Yahoo, real → mock) significava caçar chamadas HTTP espalhadas pelo código**, em vez de trocar uma implementação em um único lugar.

A saída foi isolar o **domínio** (as regras que definem o que é "preço médio" e "posição consolidada") de **tudo que é detalhe de infraestrutura** (Django ORM, brapi, BCB, geração de `.xlsx`). Esse isolamento é o princípio central da Clean Architecture de Robert Martin: dependências apontam sempre para dentro, do detalhe para a regra de negócio — nunca o contrário.

Na prática, isso significa que `core/` (o domínio) **não importa nada de Django, DRF, `requests` ou `openpyxl`**. Quem importa `core/` é a infraestrutura, e não o inverso.

```
                    depende de
   api/  ────────────────────────►  core/
   portfolio/  ─────────────────►  core/
   infrastructure/  ────────────►  core/

   core/  ──────────────────────►  (nada — zero imports de framework)
```

## Anatomia do backend

```
backend/
├── core/                        ← DOMÍNIO (a regra de negócio, e só ela)
│   ├── entities.py                 Ativo, Operacao, Posicao — dataclasses puras
│   ├── ports.py                    contratos (Protocol) que a infra deve cumprir
│   └── use_cases/                  uma classe por caso de uso, uma responsabilidade cada
│       ├── registrar_operacao.py
│       ├── consolidar_posicoes.py
│       ├── calcular_rentabilidade.py
│       ├── atualizar_cotacoes.py
│       ├── gerar_relatorio_excel.py
│       └── resumo_carteira.py
│
├── infrastructure/              ← IMPLEMENTAÇÕES CONCRETAS dos ports
│   ├── market_data/
│   │   ├── brapi_client.py         cotação atual (brapi.dev)
│   │   ├── bcb_client.py           série histórica do CDI (SGS/BCB, série 4391)
│   │   ├── yahoo_client.py         histórico mensal de preços
│   │   └── provedor.py             compõe as três fontes acima num ProvedorCotecoes
│   ├── excel/
│   │   └── openpyxl_writer.py      GeradorRelatorio via openpyxl
│   └── mock_market_data.py         ProvedorCotacoes falso, para os testes
│
├── portfolio/                   ← Django app: só ORM e tradução model ↔ entidade
│   ├── models.py                   Ativo, Operacao, Cotacao (tabelas)
│   └── repositories.py             implementa RepositorioAtivos/Operacoes/Cotacoes
│
├── api/                          ← INTERFACE HTTP: só tradução, nenhuma regra
│   ├── views.py                    valida entrada → chama use case → serializa saída
│   ├── serializers.py
│   ├── urls.py
│   └── deps.py                     ⚙ composition root: monta os use cases
│
└── tests/                        casos de uso testados sem Django, API testada com APIClient
```

Cada pasta tem **um único motivo para mudar**:

| Camada | Muda quando... | Depende de |
|---|---|---|
| `core/entities.py` | a definição de "posição" ou "operação" muda | nada |
| `core/use_cases/` | uma regra de negócio muda | `core/entities.py`, `core/ports.py` |
| `core/ports.py` | o domínio passa a precisar de um novo dado externo | `core/entities.py` |
| `infrastructure/` | a brapi muda de contrato, ou trocamos de provedor de cotação | `core/ports.py` |
| `portfolio/` | o schema do banco muda | `core/entities.py`, ORM do Django |
| `api/` | um endpoint muda de formato | `core/use_cases/`, DRF |

## O fluxo de uma requisição

Tomemos como exemplo `GET /api/carteira/rentabilidade/`, que compara a carteira do usuário contra CDI e Ibovespa:

```
1. api/urls.py           roteia para CarteiraRentabilidadeView
2. api/views.py           extrai o usuário autenticado (JWT) e delega
3. api/deps.py             monta o caso de uso, injetando as implementações concretas:
                             CalcularRentabilidade(
                                 RepositorioOperacoesDjango(usuario),   ← Postgres
                                 ProvedorCotacoesB3Bcb(),               ← brapi + BCB + Yahoo
                             )
4. core/use_cases/
   calcular_rentabilidade.py  aplica o método de Dietz modificado sobre as operações
                               e compara com as séries de CDI/Ibovespa — 100% Python puro
5. api/serializers.py     converte o resultado (dataclasses) em JSON
6. api/views.py           devolve a Response
```

A view (passo 2) e o `deps.py` (passo 3) são os **únicos pontos do sistema que sabem, ao mesmo tempo, que existe Django e que existe um caso de uso**. O caso de uso em si (passo 4) poderia rodar em um script standalone, sem Django instalado — e é exatamente isso que os testes em `tests/test_use_cases.py` fazem, substituindo `RepositorioOperacoesDjango` e `ProvedorCotacoesB3Bcb` por *fakes* em memória.

Esse padrão — view magra, injeção de dependência explícita em `deps.py`, caso de uso ignorante de framework — se repete para cada endpoint da API.

## Modelo de domínio

As entidades em `core/entities.py` carregam a lógica financeira como *properties*, não como métodos de model do Django:

- **`Operacao`** — compra ou venda de um `ticker`, com `quantidade`, `preco_unitario` e `data`. `valor_total` é derivado, nunca armazenado.
- **`Posicao`** — o resultado de consolidar todas as operações de um ativo: `quantidade` e `preco_medio` (ponderado pelas compras, preservado nas vendas). A partir da `cotacao_atual` injetada, calcula `valor_mercado`, `resultado` e `resultado_pct` — a marcação a mercado é uma função pura da posição e da cotação, não um campo persistido.
- **Erros de domínio são exceções tipadas** (`SaldoInsuficienteError`, `AtivoInexistenteError`, `FonteExternaError`), não códigos HTTP — é a camada `api/` que traduz cada uma para o status code correto.

Regras que vivem exclusivamente aqui, sem cair para SQL nem para chamadas de API:

- Preço médio ponderado nas compras; preservado (não recalculado) nas vendas.
- Validação de saldo insuficiente considerando a ordem cronológica das operações.
- Rentabilidade da carteira pelo **método de Dietz modificado**, que pondera aportes/resgates pelo tempo em que ficaram investidos dentro do período — necessário porque a carteira recebe aportes em datas diferentes e uma média simples distorceria o resultado.

## Fontes de dados de mercado

O contrato `ProvedorCotacoes` (`core/ports.py`) é implementado por `ProvedorCotacoesB3Bcb`, que compõe três fontes especializadas:

| Fonte | Uso | Client |
|---|---|---|
| **brapi.dev** | Cotação atual dos ativos e do Ibovespa (ticker `^BVSP`) | `infrastructure/market_data/brapi_client.py` |
| **Banco Central (SGS)** | Série histórica do CDI (série 4391) | `infrastructure/market_data/bcb_client.py` |
| **Yahoo Finance** | Fechamentos mensais para séries históricas | `infrastructure/market_data/yahoo_client.py` |

A escolha por **três provedores** em vez de um só reflete a realidade: nenhuma API gratuita cobre satisfatoriamente cotação em tempo real, histórico mensal e indicadores macroeconômicos ao mesmo tempo. Compor as fontes atrás de um único port mantém essa fragmentação invisível para o domínio — se amanhã a brapi mudar de contrato ou sair do ar, troca-se `brapi_client.py` sem tocar em uma linha de `core/`.

Para desenvolvimento e testes, `MockProvedorCotacoes` implementa o mesmo `Protocol` com dados simulados. A variável de ambiente `MARKET_DATA_PROVIDER` (`real` | `mock`) decide qual implementação `api/deps.py` injeta — nenhum `if` de ambiente vaza para dentro dos casos de uso.

## Frontend

SPA em **Svelte 5** (runas) + **Vite**, sem meta-framework — roteamento simples entre telas em `src/routes/` (`Landing`, `Login`, `Registro`, `Overview`, `Carteira`, `Operacoes`).

```
frontend/src/
├── lib/api/          um módulo por recurso (ativos, operacoes, posicoes, carteira,
│                      relatorios) — espelha os endpoints do backend 1:1
├── lib/components/    KpiCards, PositionsTable, OperationForm, Toast,
│   └── charts/        PerformanceChart e AllocationDonut (Chart.js),
│                       BenchmarkRuler (comparação visual com CDI/Ibovespa)
├── lib/state/          estado compartilhado com runas do Svelte 5 ($state)
└── routes/             uma tela por rota, montadas em App.svelte
```

A camada `lib/api/` existe pelo mesmo motivo que `api/` existe no backend: isolar o "como" (fetch, headers, JWT) do "o quê" (uma tela pede a posição consolidada, não sabe como o token é anexado à requisição).

## Testes

```
backend/tests/
├── test_use_cases.py   casos de uso com repositórios/provedores fake — sem Django, sem rede
├── test_api.py          endpoints via APIClient do DRF — integração real com o ORM
└── test_provedor.py     ProvedorCotacoesB3Bcb isolado
```

`conftest.py` força `MARKET_DATA_PROVIDER=mock` globalmente nos testes, garantindo que a suíte nunca dependa da brapi, do BCB ou do Yahoo estarem no ar. É a divisão em camadas que torna isso possível: como os casos de uso só conhecem `Protocol`s, um repositório em memória de algumas linhas basta para testá-los por completo.

```bash
cd backend
pytest
```

## Rodando localmente

```bash
# banco de dados
docker compose up -d

# backend
cd backend
cp .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # dados de exemplo (opcional)
python manage.py runserver

# frontend
cd frontend
npm install
npm run dev
```

## Deploy

- **Backend** — Render (`render.yaml`): `gunicorn`, Postgres gerenciado, migração automática no build.
- **Frontend** — Vercel: build estático do Vite, com rewrite de `/api/*` para o backend no Render, tornando as chamadas same-origin em produção (por isso CORS praticamente não entra em jogo fora do ambiente local).

## Decisões e trade-offs

Nenhuma arquitetura é gratuita — vale registrar os trade-offs conscientemente aceitos:

- **Mais arquivos e indireção para um projeto deste tamanho.** Um CRUD simples não justificaria portas, casos de uso e repositórios separados. A aposta foi que a combinação de regras financeiras não triviais com múltiplas integrações externas instáveis compensa o custo — e os testes em `test_use_cases.py`, que rodam em milissegundos sem tocar rede ou banco, são o retorno mais visível desse investimento.
- **`portfolio/repositories.py` só faz tradução model ↔ entidade.** Poderia ter sido incorporado a `models.py`, mas mantê-lo separado deixa explícito onde termina "o que o Django sabe" e começa "o que o domínio precisa".
- **Svelte puro em vez de SvelteKit.** Sem SSR ou roteamento por sistema de arquivos, a aplicação é uma SPA simples — decisão adequada a um dashboard autenticado, onde SEO e renderização no servidor não trazem benefício.
- **Marcação a mercado não é persistida como fato consumado** — é recalculada a partir de `Posicao.cotacao_atual` a cada leitura. Evita inconsistência entre "posição" e "cotação salva", ao custo de recalcular em toda requisição (aceitável dado o volume de dados de uma carteira pessoal).
