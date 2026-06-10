# Sistema Inteligente de Monitoramento — Missão Aurora Siger

**Global Solution — FIAP Engenharia de Software (1ESPR)**
**Período:** 25/05 a 09/06/2026

## Equipe

| Nome | RM |
|------|-----|
| Gabriel de Leão Rocha | 571330 |
| Guilherme Alves Nunes | 572754 |
| Pedro Henrique de Souza Elias | 570487 |
| Mauricio Furlan Rodrigues Chaves | 572512 |

---

## 1. Resumo do Problema

A missão **Aurora Siger** simula a operação de uma base experimental em Marte. Em
ambientes onde a comunicação com a Terra é limitada e a margem para erro é zero,
os dados gerados pelos sensores são a única fonte para tomar decisões. Este
projeto entrega um **sistema inteligente de monitoramento operacional** que:

- recebe e interpreta telemetria de 12 ciclos (módulos críticos, energia, clima);
- organiza os dados em estruturas computacionais apropriadas;
- aplica regras lógicas (AND/OR/NOT) para classificar a situação;
- gera alertas priorizados e recomendações automáticas;
- prevê o próximo ciclo com regressão linear simples;
- detecta inconsistências propositais nos dados.

O sistema integra os conteúdos das três fases anteriores do curso:

| Fase | Conteúdos reutilizados |
|------|------------------------|
| 1 | Sistemas binários, faixas seguras, pensamento computacional, IF/ELIF/ELSE |
| 2 | Filas (FIFO), pilhas (LIFO), busca linear, bubble sort, portas lógicas |
| 3 | Dicionários/hash, hierarquia, BST, matrizes, regressão linear |

---

## 2. Estruturas de Dados Usadas

Todas as 6 estruturas exigidas pelo paper estão implementadas em
[src/sistema.py](src/sistema.py):

| Estrutura | Onde | Para que |
|-----------|------|----------|
| **Lista** | séries temporais de energia, consumo, temperatura | armazenar leituras por ciclo |
| **Fila FIFO** (`FilaAlertas`) | alertas pendentes | processar alertas na ordem em que chegam |
| **Pilha LIFO** (`PilhaEventos`) | últimos eventos críticos | consultar primeiro o evento mais recente |
| **Dicionário / hash** | acesso O(1) aos 6 módulos pelo nome | `dicionario_modulos["energia"]` |
| **Árvore (hierarquia + BST)** | hierarquia missão→sistemas→subsistemas, BST por ciclo | navegar a colônia, busca O(log n) por ciclo |
| **Matriz** (lista de listas) | leituras por `ciclo × variável` | acesso bidimensional `matriz[i][j]` |

---

## 3. Regras Lógicas Principais

Expressões booleanas que governam a classificação do status da missão (estilo
**portas lógicas da Fase 2** + **motor de decisão da Fase 3**):

```
Variáveis booleanas:
  SV = suporte_vida ativo
  EN = energia ativo
  CO = comunicacao ativa
  LAB = laboratorio ativo
  RB = reserva < 20%        (reserva baixa)
  RA = reserva < 50%        (reserva em alerta)
  RD = radiação > 80        (radiação perigosa)
  CB = qualidade_com < 30%  (comunicação baixa)
  DF = consumo > geração    (déficit energético)

Regras (5+ regras com AND/OR/NOT, paper exige no mínimo 3):

R1  CRITICO = RB AND DF
R2  CRITICO = (NOT SV) OR (NOT EN)
R3  ALERTA  = (NOT CO) OR CB OR RD
R4  ALERTA  = RA AND DF
R5  ALERTA  = DF AND (NOT LAB)
R6  NORMAL  = caso contrário (fallback)
```

**Tabela de status por módulo** (classificação derivada do `% de ciclos ativos`):

| % ciclos ativo | Classificação |
|----------------|---------------|
| ≥ 90% | NORMAL |
| ≥ 50% | ALERTA |
| < 50% | CRÍTICO |

---

## 4. Técnica de Previsão

**Regressão linear simples** (método dos mínimos quadrados), reutilizada do
módulo `regression_model.py` da Fase 3. Implementação manual, sem bibliotecas
externas.

Aplicada sobre `reserva_energia_pct` (variável crítica) ao longo dos 12 ciclos:

```
β₁ = Σ[(xᵢ − x̄)(yᵢ − ȳ)] / Σ[(xᵢ − x̄)²]
β₀ = ȳ − β₁ · x̄
ŷ_próximo = β₀ + β₁ · (ciclo + 1)
```

A previsão **influencia diretamente** a recomendação automática:

- `ŷ < 20%` → emite **alerta preventivo CRÍTICO** antes do próximo ciclo
- `ŷ < 50%` → emite **alerta preventivo ALERTA** com sugestão de redução
- caso contrário → operação normal

Resultado nos dados atuais: **R² = 0.9924** (ajuste excelente), reserva projetada
para o ciclo 13 = **12.67%** → recomendação automática **CRÍTICA**.

---

## 5. Inconsistência Proposital

O ciclo 8 contém uma inconsistência intencional para validar o diagnóstico:

| Campo | Valor |
|-------|-------|
| `comunicacao` | 1 (módulo reportado ATIVO) |
| `qualidade_comunicacao_pct` | 0 (sinal nulo) |

A função `detectar_inconsistencias()` identifica que essas duas leituras são
contraditórias (sensor reportando dados conflitantes) e gera um diagnóstico.

---

## 6. Como Executar

**Requisitos:** Python 3.10+ (uso de type hints `X | None`; não usa bibliotecas
externas, apenas `csv`, `os` e `tkinter` da biblioteca padrão — `tkinter` é
opcional, usado só pela interface gráfica).

### Modo terminal (CLI)

```bash
git clone https://github.com/GabrielLeaoRocha/Global-Sollution-Semestre-1.git
cd Global-Sollution-Semestre-1
python3 src/sistema.py        # ou: python3 -m src.sistema
```

### Modo interface gráfica (GUI nativa)

Um dashboard `tkinter` seguindo o **Aurora Siger Tkinter Style Guide** —
paleta oficial (`#e90061` rosa / `#1e1e1e` cinza / `#f8f8f8` branco),
sidebar com indicador de ativo, KPI cards com acento rosa, tabelas
`ttk.Treeview` com seleção rosa, e **gráfico de regressão linear**
desenhado nativamente no `tk.Canvas` (sem matplotlib).

```bash
python3 -m src.interface_grafica       # abre direto
# ou: digite [g] no menu da CLI
```

**10 telas no dashboard:**
Resumo (KPI cards), Módulos, Alertas, Pilha (LIFO), Hierarquia,
Matriz, Previsão (com gráfico nativo), Diagnóstico, Log, Buscar (BST + módulo).

> ⚠️ **Nota sobre `tkinter`:** o `tkinter` faz parte da biblioteca padrão, mas
> algumas distribuições do Python (ex: Python via Homebrew no macOS) não o
> incluem por padrão. Use o Python oficial do
> [python.org](https://www.python.org/downloads/) ou instale via:
> `brew install python-tk` (macOS) ou `sudo apt install python3-tk` (Debian/Ubuntu).
> A CLI funciona em qualquer Python.

### Menu interativo

```
[ 1] Resumo da missao
[ 2] Tabela de status dos modulos
[ 3] Alertas priorizados
[ 4] Pilha de eventos criticos
[ 5] Hierarquia da missao
[ 6] Matriz de leituras
[ 7] Previsao (regressao linear)
[ 8] Inconsistencias detectadas
[ 9] Log completo de eventos
[10] Buscar ciclo na BST
[11] Buscar modulo pelo nome
[ 0] Executar TUDO (relatorio completo)
[ q] Sair
```

A opção **0** roda o pipeline completo (recomendado para validação rápida).

---

## 7. Exemplo de Entrada e Saída

### Entrada — `data/telemetria_missao.csv` (extrato)

```
ciclo,suporte_vida,energia,comunicacao,...,reserva_energia_pct,radiacao_nivel,...
1,1,1,1,...,85.0,22.0,...
...
8,1,1,1,...,46.0,68.0,...           ← inconsistência: qualidade_com = 0
...
12,1,1,0,...,16.0,92.0,...          ← cenário crítico
```

### Saída — Cenário NORMAL (ciclo 1)

```
[1] suporte_vida    ATIVO
[1] energia         ATIVO
Status: NORMAL — todos os parâmetros dentro da faixa segura.
```

### Saída — Cenário CRÍTICO (ciclo 12)

```
ALERTAS ATIVOS (5 no total)

[1] CICLO 12 | CRITICO  | R1: reserva<20% AND consumo>geracao
    -> Reserva critica com deficit energetico
    ACAO: Ativar modo emergencia - desligar todos os sistemas
          nao essenciais, manter suporte a vida

PREVISAO - REGRESSAO LINEAR (reserva energetica)
  Modelo:           y = 95.6667 + -6.3846 * x
  R^2:              0.9924
  Reserva prevista: 12.67%
  >> PREVENTIVO CRITICO: reserva projetada abaixo de 20%.
     Acionar protocolo de emergencia ANTES do proximo ciclo.

INCONSISTENCIAS DETECTADAS (1)
  ciclo 8 | SENSOR_CONFLITANTE | comunicacao=1 mas qualidade=0
```

---

## 8. Estrutura do Repositório

O código foi organizado em **pacotes Python por responsabilidade**, seguindo
boas práticas (separação de concerns, `__init__.py` com re-exports, type hints,
docstrings de módulo). O entrypoint exigido pelo paper (`src/sistema.py`) atua
como orquestrador.

```
Global-Sollution-Semestre-1/
├── README.md
├── .gitignore
├── data/
│   ├── telemetria_missao.csv         12 ciclos × 15 colunas
│   └── log_eventos.csv               10 eventos
├── src/
│   ├── sistema.py                    entrypoint — main(), menu, pipeline
│   ├── config.py                     constantes (faixas seguras, severidades)
│   ├── estruturas/                   estruturas de dados (Fase 2 + Fase 3)
│   │   ├── __init__.py
│   │   ├── fila.py                   FilaAlertas (FIFO)
│   │   ├── pilha.py                  PilhaEventos (LIFO)
│   │   ├── bst.py                    Binary Search Tree por ciclo
│   │   └── algoritmos.py             busca linear + bubble sort
│   ├── dados/                        I/O e organização (Fase 3)
│   │   ├── __init__.py
│   │   ├── loader.py                 carregar_csv, carregar_telemetria
│   │   └── organizacao.py            dicionário, hierarquia, matriz
│   ├── logica/                       regras de negócio
│   │   ├── __init__.py
│   │   ├── regras.py                 avaliar_ciclo (AND/OR/NOT)
│   │   ├── alertas.py                gerar/priorizar/enfileirar
│   │   └── diagnostico.py            classificação + inconsistências
│   ├── previsao/                     análise estatística
│   │   ├── __init__.py
│   │   └── regressao.py              regressão linear simples
│   ├── exibicao/                     camada de apresentação
│   │   ├── __init__.py
│   │   └── relatorios.py             funções de display no terminal
│   ├── gui/                          dashboard tkinter (style guide oficial)
│   │   ├── __init__.py
│   │   ├── theme.py                  paleta, fontes, ttk.Style global
│   │   ├── widgets.py                make_kpi_card, make_nav_item, status_dot
│   │   └── charts.py                 gráfico de linha nativo no Canvas
│   └── interface_grafica.py          dashboard principal (orquestra src/gui)
└── docs/
    ├── relatorio.pdf                 (a entregar)
    ├── link_video.txt                (a entregar)
    └── uso_ia.md                     (a entregar)
```

### Boas práticas aplicadas

- **Separação por responsabilidade** — cada pacote isolado por domínio (dados,
  lógica, previsão, exibição, estruturas).
- **API pública explícita** via `__all__` nos `__init__.py`.
- **Type hints** em todas as assinaturas (`list[dict]`, `tuple[float, float]`,
  `X | None`).
- **Docstrings de módulo e função** explicando origem (Fase 2 / Fase 3) e
  invariantes.
- **Constantes centralizadas** em `config.py` (`Final[T]`) — facilita ajuste
  de faixas sem tocar na lógica.
- **`__slots__`** em `NoBST` para reduzir overhead de memória.
- **Funções privadas** com prefixo `_` (ex: `_extrair_booleanas`,
  `_classificar_previsao`).
- **Imports absolutos** (`from src.X import Y`) — robustos e claros.

---

## 9. Mapeamento de Conteúdos Integrados

| Conteúdo (paper §5) | Onde aparece no código |
|--------------------|-------------------------|
| Sistemas binários (F1) | `config.MODULOS_CRITICOS` + status 0/1 em `logica/regras.py` |
| IF/ELIF/ELSE (F1) | `logica/regras.py::avaliar_ciclo` |
| Faixas seguras (F1) | `config.py` — `RESERVA_*`, `RADIACAO_*`, `COMUNICACAO_*` |
| Portas lógicas AND/OR/NOT (F2) | regras R1–R5 em `logica/regras.py` |
| Fila FIFO (F2) | `estruturas/fila.py::FilaAlertas` |
| Pilha LIFO (F2) | `estruturas/pilha.py::PilhaEventos` |
| Busca linear (F2) | `estruturas/algoritmos.py::buscar_modulo_por_nome` |
| Bubble sort (F2) | `estruturas/algoritmos.py::ordenar_alertas_por_severidade` |
| Dicionário / hash (F3) | `dados/organizacao.py::construir_dicionario_modulos` |
| Hierarquia (F3) | `dados/organizacao.py::construir_hierarquia` |
| BST (F3) | `estruturas/bst.py` (`NoBST`, `inserir_bst`, `buscar_bst`, `construir_bst_balanceada`) |
| Matriz (F3) | `dados/organizacao.py::construir_matriz_leituras` |
| Análise de dados (F3) | `previsao/regressao.py` (`regressao_linear`, `prever`, `r_quadrado`) |
| Sustentabilidade (F1/F2/F3) | geração solar + eólica, gestão de reserva |

---

## 10. Vídeo de Apresentação

Link do vídeo (YouTube, "Não Listado"):

> https://www.youtube.com/watch?v=KVR3lpWPoi0

---

## 11. Restrições Atendidas

- ✅ Python puro — somente `csv` e `os` da stdlib
- ✅ Entrypoint `src/sistema.py` exigido pelo paper
- ✅ Dados em CSV externo legível (`data/*.csv`)
- ✅ Executa sem erros via `python3 src/sistema.py` ou `python3 -m src.sistema`
- ✅ Código comentado, funções com docstrings e type hints
