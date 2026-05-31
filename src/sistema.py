"""
sistema.py - Sistema Inteligente de Monitoramento da Missao Aurora Siger

Global Solution - FIAP Engenharia de Software 1ESPR
RM 571330 - Gabriel de Leao Rocha

Integra conhecimentos das tres fases anteriores:
  Fase 1: sistemas numericos (status binarios), if/elif/else, faixas seguras,
          analise energetica, pensamento computacional.
  Fase 2: portas logicas (AND/OR/NOT), filas (FIFO), pilhas (LIFO),
          busca linear, bubble sort.
  Fase 3: dicionarios/hash, hierarquia, BST, matrizes, regressao linear.

Restricao: Python puro (apenas csv e os).
Execucao:  python3 src/sistema.py
"""

import csv
import os


# =============================================================================
# CONSTANTES E FAIXAS DE SEGURANCA  (origem: Fase 1 - faixas-seguras.md)
# =============================================================================

# Reserva energetica (%)
RESERVA_CRITICA = 20.0
RESERVA_ALERTA = 50.0

# Radiacao (escala 0-100)
RADIACAO_CRITICA = 80.0
RADIACAO_ALERTA = 60.0

# Qualidade de comunicacao (%)
COMUNICACAO_CRITICA = 30.0
COMUNICACAO_ALERTA = 70.0

# Temperatura externa (Celsius) - limites operacionais Marte
TEMPERATURA_MIN_SEGURA = -70.0

# Severidades (numero menor = mais urgente, para ordenacao)
SEV_CRITICO = 1
SEV_ALERTA = 2
SEV_NORMAL = 3

# Nomes dos 6 modulos criticos
MODULOS_CRITICOS = [
    "suporte_vida",
    "energia",
    "comunicacao",
    "habitat",
    "laboratorio",
    "armazenamento",
]


# =============================================================================
# ESTRUTURAS DE DADOS  (origem: Fase 2 - estruturas.py)
# =============================================================================

class FilaAlertas:
    """Fila FIFO de alertas pendentes (adaptada de FilaPouso, Fase 2).

    Primeiro alerta gerado e o primeiro a ser processado pelo operador.
    """

    def __init__(self):
        self._fila = []

    def enqueue(self, alerta):
        """Adiciona alerta no final da fila."""
        self._fila.append(alerta)

    def dequeue(self):
        """Remove e retorna o alerta mais antigo."""
        if self.is_empty():
            return None
        return self._fila.pop(0)

    def front(self):
        """Retorna o proximo alerta sem remover."""
        if self.is_empty():
            return None
        return self._fila[0]

    def is_empty(self):
        return len(self._fila) == 0

    def size(self):
        return len(self._fila)

    def listar(self):
        return list(self._fila)


class PilhaEventos:
    """Pilha LIFO dos ultimos eventos criticos (reutilizada de PilhaHistorico,
    Fase 2). Ultimo evento empilhado e o primeiro consultado."""

    def __init__(self):
        self._pilha = []

    def push(self, evento):
        self._pilha.append(evento)

    def pop(self):
        if self.is_empty():
            return None
        return self._pilha.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self._pilha[-1]

    def is_empty(self):
        return len(self._pilha) == 0

    def size(self):
        return len(self._pilha)

    def listar(self):
        """Retorna copia com o topo (mais recente) primeiro."""
        return list(reversed(self._pilha))


# Busca linear (Fase 2 - buscar_por_id adaptada)
def buscar_modulo_por_nome(dicionario_modulos, nome):
    """Busca linear O(n) por nome de modulo no dicionario hash."""
    for chave, valor in dicionario_modulos.items():
        if chave == nome:
            return valor
    return None


# Bubble sort (Fase 2 - ordenar_por_prioridade adaptado)
def ordenar_alertas_por_severidade(lista_alertas):
    """Bubble sort O(n^2) - ordena alertas por severidade (CRITICO primeiro).

    Justificativa: algoritmo simples e previsivel, adequado para volume pequeno
    de alertas (tipicamente < 50) que ocorre em uma missao.
    """
    copia = list(lista_alertas)
    n = len(copia)
    for i in range(n):
        trocou = False
        for j in range(0, n - i - 1):
            if copia[j]["severidade_num"] > copia[j + 1]["severidade_num"]:
                copia[j], copia[j + 1] = copia[j + 1], copia[j]
                trocou = True
        if not trocou:
            break
    return copia


# BST (Fase 3 - binary_tree.py) - indexacao por ciclo
class NoBST:
    """No da arvore binaria de busca indexada por ciclo de medicao."""

    def __init__(self, ciclo, dados):
        self.ciclo = ciclo
        self.dados = dados
        self.esquerda = None
        self.direita = None


def inserir_bst(raiz, ciclo, dados):
    """Insere no na BST recursivamente."""
    if raiz is None:
        return NoBST(ciclo, dados)
    if ciclo < raiz.ciclo:
        raiz.esquerda = inserir_bst(raiz.esquerda, ciclo, dados)
    elif ciclo > raiz.ciclo:
        raiz.direita = inserir_bst(raiz.direita, ciclo, dados)
    else:
        raiz.dados = dados
    return raiz


def buscar_bst(raiz, ciclo):
    """Busca O(log n) por ciclo na BST."""
    if raiz is None:
        return None
    if ciclo == raiz.ciclo:
        return raiz.dados
    if ciclo < raiz.ciclo:
        return buscar_bst(raiz.esquerda, ciclo)
    return buscar_bst(raiz.direita, ciclo)


def construir_bst_balanceada(leituras):
    """Constroi BST balanceada inserindo pelo elemento mediano."""
    if not leituras:
        return None
    ordenadas = sorted(leituras, key=lambda r: r["ciclo"])
    return _construir_balanceada(ordenadas, 0, len(ordenadas) - 1)


def _construir_balanceada(lista, ini, fim):
    if ini > fim:
        return None
    meio = (ini + fim) // 2
    no = NoBST(lista[meio]["ciclo"], lista[meio])
    no.esquerda = _construir_balanceada(lista, ini, meio - 1)
    no.direita = _construir_balanceada(lista, meio + 1, fim)
    return no


# =============================================================================
# LEITURA DE DADOS  (origem: Fase 3 - data_loader.py / load_csv)
# =============================================================================

def carregar_csv(caminho):
    """Le um CSV e retorna lista de dicionarios com tipos convertidos.

    Adaptada de load_csv() (Fase 3). Conversao automatica:
      - inteiros (sem ponto decimal)
      - floats (com ponto decimal)
      - strings (fallback)
    """
    registros = []
    with open(caminho, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            convertida = {}
            for chave, valor in linha.items():
                try:
                    convertida[chave] = int(valor) if "." not in valor else float(valor)
                except ValueError:
                    convertida[chave] = valor
            registros.append(convertida)
    return registros


def carregar_telemetria():
    """Carrega data/telemetria_missao.csv."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return carregar_csv(os.path.join(base, "data", "telemetria_missao.csv"))


def carregar_log_eventos():
    """Carrega data/log_eventos.csv."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return carregar_csv(os.path.join(base, "data", "log_eventos.csv"))


# =============================================================================
# ORGANIZACAO DOS DADOS  (origem: Fase 3 - build_colony_structure)
# =============================================================================

def construir_dicionario_modulos(telemetria):
    """Dicionario/hash com acesso O(1) ao status agregado de cada modulo.

    Para cada modulo, calcula:
      - total de ciclos ativo (status=1)
      - total de ciclos inativo (status=0)
      - lista historica de status
      - status atual (ultimo ciclo)
    """
    modulos = {}
    for nome in MODULOS_CRITICOS:
        historico = [registro[nome] for registro in telemetria]
        modulos[nome] = {
            "nome": nome,
            "historico": historico,
            "status_atual": historico[-1],
            "ciclos_ativo": sum(historico),
            "ciclos_inativo": len(historico) - sum(historico),
        }
    return modulos


def construir_hierarquia(telemetria):
    """Constroi hierarquia da missao (adaptada de build_colony_structure, Fase 3).

    Nivel 0: Missao Aurora Siger
    Nivel 1: Sistemas (energia, habitat, operacional)
    Nivel 2: Subsistemas/recursos
    """
    return {
        "missao": "Aurora Siger",
        "sistemas": {
            "energia": {
                "solar": {
                    "geracao_kwh": [r["geracao_solar_kwh"] for r in telemetria],
                    "status": "ativo",
                },
                "eolica": {
                    "geracao_kwh": [r["geracao_eolica_kwh"] for r in telemetria],
                    "status": "ativo",
                },
                "bateria": {
                    "reserva_pct": [r["reserva_energia_pct"] for r in telemetria],
                    "status": "ativo",
                },
            },
            "habitat": {
                "oxigenio": {"modulo_referencia": "suporte_vida"},
                "temperatura": {
                    "leituras_c": [r["temperatura_externa_c"] for r in telemetria],
                },
                "comunicacao": {
                    "qualidade_pct": [r["qualidade_comunicacao_pct"] for r in telemetria],
                },
            },
            "operacional": {
                "laboratorio": {"modulo_referencia": "laboratorio"},
                "armazenamento": {"modulo_referencia": "armazenamento"},
            },
        },
    }


def construir_matriz_leituras(telemetria):
    """Matriz (lista de listas) [ciclo][variavel].

    Cada linha representa um ciclo, cada coluna uma variavel numerica.
    Permite acesso bidimensional matriz[i][j].
    """
    colunas = [
        "geracao_solar_kwh",
        "geracao_eolica_kwh",
        "consumo_total_kwh",
        "reserva_energia_pct",
        "temperatura_externa_c",
        "radiacao_nivel",
        "qualidade_comunicacao_pct",
        "velocidade_vento_ms",
    ]
    matriz = []
    for registro in telemetria:
        linha = [registro[coluna] for coluna in colunas]
        matriz.append(linha)
    return matriz, colunas


# =============================================================================
# REGRAS LOGICAS  (origem: Fase 2 decisao.py + Fase 3 decision_engine.py)
# =============================================================================

def avaliar_ciclo(registro):
    """Avalia o status operacional de UM ciclo da telemetria.

    Aplica regras booleanas AND/OR/NOT para classificar em:
      - CRITICO: situacao de emergencia, acao imediata
      - ALERTA:  anomalia detectada, requer atencao
      - NORMAL:  parametros dentro da faixa segura

    Variaveis booleanas (estilo Fase 2):
      SV = suporte a vida ativo
      EN = modulo de energia ativo
      CO = comunicacao ativa
      RB = reserva baixa (< 20%)
      RA = reserva em alerta (< 50%)
      RD = radiacao perigosa (> 80)
      CB = comunicacao com qualidade baixa (< 30%)
      DF = deficit energetico (consumo > geracao)

    Expressoes booleanas principais:
      CRITICO = RB AND DF                       (regra 1 - emergencia energetica)
      CRITICO = (NOT SV) OR (NOT EN)            (regra 2 - falha de modulo vital)
      ALERTA  = (NOT CO) OR CB OR RD            (regra 3 - comunicacao/radiacao)
      ALERTA  = RA AND DF                       (regra 4 - sobrecarga moderada)
      ALERTA  = DF AND (NOT laboratorio_ativo)  (regra 5 - consumo elevado sem lab)
    """
    # Variaveis booleanas
    sv = registro["suporte_vida"] == 1
    en = registro["energia"] == 1
    co = registro["comunicacao"] == 1
    ha = registro["habitat"] == 1
    lab = registro["laboratorio"] == 1
    arm = registro["armazenamento"] == 1

    reserva = registro["reserva_energia_pct"]
    consumo = registro["consumo_total_kwh"]
    geracao = registro["geracao_solar_kwh"] + registro["geracao_eolica_kwh"]
    radiacao = registro["radiacao_nivel"]
    qual_com = registro["qualidade_comunicacao_pct"]

    rb = reserva < RESERVA_CRITICA          # reserva baixa
    ra = reserva < RESERVA_ALERTA           # reserva em alerta
    rd = radiacao > RADIACAO_CRITICA        # radiacao perigosa
    cb = qual_com < COMUNICACAO_CRITICA     # comunicacao baixa
    df = consumo > geracao                  # deficit energetico

    # Regras AND/OR/NOT (if/elif/else encadeado, ordem por prioridade)
    if rb and df:
        return {
            "ciclo": registro["ciclo"],
            "status": "CRITICO",
            "severidade_num": SEV_CRITICO,
            "regra": "R1: reserva<20% AND consumo>geracao",
            "descricao": "Reserva critica com deficit energetico",
            "acao": "Ativar modo emergencia - desligar todos os sistemas nao essenciais, manter suporte a vida",
        }

    if (not sv) or (not en):
        return {
            "ciclo": registro["ciclo"],
            "status": "CRITICO",
            "severidade_num": SEV_CRITICO,
            "regra": "R2: (NOT suporte_vida) OR (NOT energia)",
            "descricao": "Falha em modulo vital",
            "acao": "Acionar protocolo de emergencia - intervencao manual urgente",
        }

    if (not co) or cb or rd:
        motivos = []
        if not co:
            motivos.append("modulo comunicacao inativo")
        if cb:
            motivos.append("qualidade do sinal abaixo de 30%")
        if rd:
            motivos.append("radiacao acima de 80")
        return {
            "ciclo": registro["ciclo"],
            "status": "ALERTA",
            "severidade_num": SEV_ALERTA,
            "regra": "R3: (NOT comunicacao) OR comunicacao_baixa OR radiacao_alta",
            "descricao": "Comunicacao/radiacao comprometidas: " + ", ".join(motivos),
            "acao": "Ativar comunicacao de emergencia e recolher equipamentos expostos",
        }

    if ra and df:
        return {
            "ciclo": registro["ciclo"],
            "status": "ALERTA",
            "severidade_num": SEV_ALERTA,
            "regra": "R4: reserva<50% AND consumo>geracao",
            "descricao": "Reserva moderada com deficit energetico",
            "acao": "Desligar laboratorio e sistemas nao essenciais para preservar reserva",
        }

    if df and (not lab):
        return {
            "ciclo": registro["ciclo"],
            "status": "ALERTA",
            "severidade_num": SEV_ALERTA,
            "regra": "R5: consumo>geracao AND (NOT laboratorio)",
            "descricao": "Consumo elevado mesmo com laboratorio desligado",
            "acao": "Revisar habitat e sistemas auxiliares - possivel vazamento",
        }

    return {
        "ciclo": registro["ciclo"],
        "status": "NORMAL",
        "severidade_num": SEV_NORMAL,
        "regra": "fallback: nenhuma condicao critica",
        "descricao": "Todos os parametros dentro da faixa segura",
        "acao": "Operacao normal - sem acao necessaria",
    }


def classificar_modulos(dicionario_modulos):
    """Tabela de status dos 6 modulos criticos (normal/alerta/critico).

    Criterio: percentual de ciclos em que o modulo esteve ativo.
      >= 90% ativo -> NORMAL
      >= 50% ativo -> ALERTA
      <  50% ativo -> CRITICO
    """
    tabela = {}
    for nome, dados in dicionario_modulos.items():
        total = len(dados["historico"])
        pct_ativo = (dados["ciclos_ativo"] / total) * 100 if total > 0 else 0
        if pct_ativo >= 90:
            status = "NORMAL"
        elif pct_ativo >= 50:
            status = "ALERTA"
        else:
            status = "CRITICO"
        tabela[nome] = {
            "status": status,
            "pct_ativo": round(pct_ativo, 1),
            "status_atual": dados["status_atual"],
        }
    return tabela


def detectar_inconsistencias(telemetria):
    """Diagnostico de leituras conflitantes nos dados.

    Detecta:
      - comunicacao ativa (=1) mas qualidade_comunicacao_pct == 0
      - energia ativa (=1) mas reserva == 0
      - suporte_vida ativo mas consumo abaixo do minimo vital (< 10 kWh)
    """
    inconsistencias = []
    for registro in telemetria:
        ciclo = registro["ciclo"]
        if registro["comunicacao"] == 1 and registro["qualidade_comunicacao_pct"] == 0:
            inconsistencias.append({
                "ciclo": ciclo,
                "tipo": "SENSOR_CONFLITANTE",
                "descricao": "Modulo comunicacao=1 mas qualidade=0 (sensor reportando dados conflitantes)",
            })
        if registro["energia"] == 1 and registro["reserva_energia_pct"] == 0:
            inconsistencias.append({
                "ciclo": ciclo,
                "tipo": "SENSOR_CONFLITANTE",
                "descricao": "Modulo energia=1 mas reserva=0 (falha de leitura)",
            })
        if registro["suporte_vida"] == 1 and registro["consumo_total_kwh"] < 10:
            inconsistencias.append({
                "ciclo": ciclo,
                "tipo": "CONSUMO_SUSPEITO",
                "descricao": "Suporte a vida ativo com consumo total < 10 kWh (anomalia)",
            })
    return inconsistencias


# =============================================================================
# ALERTAS AUTOMATICOS
# =============================================================================

def gerar_alertas(telemetria):
    """Gera alertas para cada ciclo aplicando as regras logicas.

    Retorna apenas os alertas com severidade ALERTA ou CRITICO.
    """
    alertas = []
    for registro in telemetria:
        avaliacao = avaliar_ciclo(registro)
        if avaliacao["severidade_num"] <= SEV_ALERTA:
            alertas.append(avaliacao)
    return alertas


def priorizar_alertas(lista_alertas):
    """Ordena alertas por severidade (bubble sort, Fase 2)."""
    return ordenar_alertas_por_severidade(lista_alertas)


def enfileirar_alertas(lista_alertas):
    """Coloca alertas em FilaAlertas (FIFO por ordem de chegada)."""
    fila = FilaAlertas()
    for alerta in lista_alertas:
        fila.enqueue(alerta)
    return fila


def empilhar_eventos_criticos(log_eventos):
    """Empilha eventos CRITICOS do log na PilhaEventos (LIFO)."""
    pilha = PilhaEventos()
    for evento in log_eventos:
        if evento["severidade"] == "CRITICO":
            pilha.push(evento)
    return pilha


# =============================================================================
# PREVISAO  (origem: Fase 3 - regression_model.py)
# =============================================================================

def media(valores):
    """Media aritmetica."""
    return sum(valores) / len(valores)


def regressao_linear(x_vals, y_vals):
    """Regressao linear simples por minimos quadrados (reutilizada Fase 3).

    Formulas:
      beta_1 = SUM[(x - x_med)(y - y_med)] / SUM[(x - x_med)^2]
      beta_0 = y_med - beta_1 * x_med

    Retorna: (beta_0, beta_1)
    """
    n = len(x_vals)
    x_med = media(x_vals)
    y_med = media(y_vals)

    numerador = 0.0
    denominador = 0.0
    for i in range(n):
        dx = x_vals[i] - x_med
        dy = y_vals[i] - y_med
        numerador += dx * dy
        denominador += dx * dx

    if denominador == 0:
        return (y_med, 0.0)

    beta_1 = numerador / denominador
    beta_0 = y_med - beta_1 * x_med
    return (beta_0, beta_1)


def prever(x, beta_0, beta_1):
    """y = beta_0 + beta_1 * x."""
    return beta_0 + beta_1 * x


def r_quadrado(x_vals, y_vals, beta_0, beta_1):
    """Coeficiente de determinacao R^2."""
    y_med = media(y_vals)
    ss_res = 0.0
    ss_tot = 0.0
    for i in range(len(x_vals)):
        y_pred = prever(x_vals[i], beta_0, beta_1)
        ss_res += (y_vals[i] - y_pred) ** 2
        ss_tot += (y_vals[i] - y_med) ** 2
    if ss_tot == 0:
        return 0.0
    return 1 - (ss_res / ss_tot)


def prever_proximo_ciclo(telemetria):
    """Aplica regressao linear sobre reserva_energia_pct para prever proximo ciclo.

    A previsao influencia recomendacao automatica:
      - reserva prevista < 20% -> alerta preventivo CRITICO
      - reserva prevista < 50% -> alerta preventivo ALERTA
    """
    x_vals = [r["ciclo"] for r in telemetria]
    y_vals = [r["reserva_energia_pct"] for r in telemetria]
    beta_0, beta_1 = regressao_linear(x_vals, y_vals)
    r2 = r_quadrado(x_vals, y_vals, beta_0, beta_1)

    proximo_ciclo = x_vals[-1] + 1
    reserva_prevista = prever(proximo_ciclo, beta_0, beta_1)

    if reserva_prevista < RESERVA_CRITICA:
        recomendacao = "PREVENTIVO CRITICO: reserva projetada abaixo de 20%. Acionar protocolo de emergencia ANTES do proximo ciclo."
        nivel = "CRITICO"
    elif reserva_prevista < RESERVA_ALERTA:
        recomendacao = "PREVENTIVO ALERTA: reserva projetada abaixo de 50%. Desligar sistemas nao essenciais preventivamente."
        nivel = "ALERTA"
    else:
        recomendacao = "Reserva projetada dentro da faixa segura."
        nivel = "NORMAL"

    return {
        "beta_0": round(beta_0, 4),
        "beta_1": round(beta_1, 4),
        "r_quadrado": round(r2, 4),
        "proximo_ciclo": proximo_ciclo,
        "reserva_prevista_pct": round(reserva_prevista, 2),
        "recomendacao": recomendacao,
        "nivel": nivel,
    }


# =============================================================================
# EXIBICAO
# =============================================================================

def cabecalho(titulo):
    """Imprime cabecalho formatado."""
    print()
    print("=" * 70)
    print(f"  {titulo}")
    print("=" * 70)


def exibir_resumo_missao(telemetria, dicionario_modulos):
    """Resumo geral da missao."""
    cabecalho("RESUMO DA MISSAO - AURORA SIGER")
    print(f"  Ciclos analisados:       {len(telemetria)}")
    print(f"  Geracao solar media:     {media([r['geracao_solar_kwh'] for r in telemetria]):.2f} kWh")
    print(f"  Geracao eolica media:    {media([r['geracao_eolica_kwh'] for r in telemetria]):.2f} kWh")
    print(f"  Consumo medio:           {media([r['consumo_total_kwh'] for r in telemetria]):.2f} kWh")
    print(f"  Reserva atual:           {telemetria[-1]['reserva_energia_pct']:.1f}%")
    print(f"  Temperatura externa:     {telemetria[-1]['temperatura_externa_c']:.1f} C")
    print(f"  Radiacao atual:          {telemetria[-1]['radiacao_nivel']:.1f}")
    print()
    print("  Status dos modulos no ultimo ciclo:")
    for nome in MODULOS_CRITICOS:
        status_bin = dicionario_modulos[nome]["status_atual"]
        rotulo = "ATIVO" if status_bin == 1 else "INATIVO"
        print(f"    [{status_bin}] {nome:<16s} {rotulo}")


def exibir_tabela_modulos(tabela_status):
    """Tabela de classificacao dos modulos."""
    cabecalho("TABELA DE STATUS DOS MODULOS (% ciclos ativos)")
    print(f"  {'MODULO':<18s} {'STATUS':<10s} {'% ATIVO':<10s} {'ATUAL':<8s}")
    print(f"  {'-'*18} {'-'*10} {'-'*10} {'-'*8}")
    for nome, info in tabela_status.items():
        atual = "1" if info["status_atual"] == 1 else "0"
        print(f"  {nome:<18s} {info['status']:<10s} {info['pct_ativo']:<10.1f} {atual:<8s}")


def exibir_alertas(alertas_priorizados, fila_alertas):
    """Exibe alertas ordenados por severidade e fila FIFO."""
    cabecalho(f"ALERTAS ATIVOS ({len(alertas_priorizados)} no total)")
    if not alertas_priorizados:
        print("  Nenhum alerta ativo.")
        return

    print("  Ordenados por severidade (mais critico primeiro):")
    print()
    for i, alerta in enumerate(alertas_priorizados, 1):
        print(f"  [{i}] CICLO {alerta['ciclo']:>2d} | {alerta['status']:<8s} | {alerta['regra']}")
        print(f"      -> {alerta['descricao']}")
        print(f"      ACAO: {alerta['acao']}")
        print()

    print(f"  Fila FIFO (proximo a processar): ciclo {fila_alertas.front()['ciclo']}")
    print(f"  Total na fila: {fila_alertas.size()}")


def exibir_pilha_eventos(pilha_eventos):
    """Mostra eventos criticos em ordem LIFO."""
    cabecalho(f"PILHA DE EVENTOS CRITICOS ({pilha_eventos.size()} eventos)")
    if pilha_eventos.is_empty():
        print("  Nenhum evento critico empilhado.")
        return
    for i, evento in enumerate(pilha_eventos.listar(), 1):
        marca = "TOPO ->" if i == 1 else "       "
        print(f"  {marca} ciclo {evento['ciclo']:>2d} | {evento['modulo']:<14s} | {evento['descricao']}")


def exibir_hierarquia(hierarquia):
    """Mostra hierarquia da missao (arvore)."""
    cabecalho("HIERARQUIA DA MISSAO")
    print(f"  {hierarquia['missao']}")
    for sistema, conteudo in hierarquia["sistemas"].items():
        print(f"    |- {sistema}")
        for subsistema in conteudo.keys():
            print(f"    |    |- {subsistema}")


def exibir_matriz(matriz, colunas):
    """Mostra a matriz de leituras [ciclo][variavel]."""
    cabecalho("MATRIZ DE LEITURAS (ciclo x variavel)")
    cabecalhos = ["CICLO"] + [c[:12] for c in colunas]
    print("  " + " ".join(f"{h:>13s}" for h in cabecalhos))
    print("  " + "-" * (14 * len(cabecalhos)))
    for i, linha in enumerate(matriz, 1):
        valores = [f"{i:>13d}"] + [f"{v:>13.2f}" for v in linha]
        print("  " + " ".join(valores))


def exibir_previsao(previsao):
    """Mostra resultado da regressao linear e recomendacao."""
    cabecalho("PREVISAO - REGRESSAO LINEAR (reserva energetica)")
    print(f"  Modelo:                  y = {previsao['beta_0']:.4f} + {previsao['beta_1']:.4f} * x")
    print(f"  R^2 (qualidade do ajuste): {previsao['r_quadrado']:.4f}")
    print(f"  Proximo ciclo:           {previsao['proximo_ciclo']}")
    print(f"  Reserva prevista:        {previsao['reserva_prevista_pct']:.2f}%")
    print(f"  Nivel:                   {previsao['nivel']}")
    print(f"  Recomendacao:")
    print(f"    >> {previsao['recomendacao']}")


def exibir_inconsistencias(inconsistencias):
    """Mostra inconsistencias detectadas nos dados."""
    cabecalho(f"INCONSISTENCIAS DETECTADAS ({len(inconsistencias)})")
    if not inconsistencias:
        print("  Nenhuma inconsistencia detectada.")
        return
    for inc in inconsistencias:
        print(f"  ciclo {inc['ciclo']:>2d} | {inc['tipo']:<22s} | {inc['descricao']}")


def exibir_log_eventos(log_eventos):
    """Mostra o log completo de eventos."""
    cabecalho(f"LOG DE EVENTOS ({len(log_eventos)} registros)")
    print(f"  {'ID':<4s} {'CICLO':<6s} {'TIPO':<22s} {'MODULO':<14s} {'SEV':<10s}")
    print("  " + "-" * 66)
    for ev in log_eventos:
        print(f"  {str(ev['id']):<4s} {str(ev['ciclo']):<6s} {ev['tipo']:<22s} {ev['modulo']:<14s} {ev['severidade']:<10s}")


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def executar_pipeline_completo():
    """Executa todo o pipeline de uma vez (uso nao-interativo)."""
    telemetria = carregar_telemetria()
    log_eventos = carregar_log_eventos()

    dicionario_modulos = construir_dicionario_modulos(telemetria)
    hierarquia = construir_hierarquia(telemetria)
    matriz, colunas = construir_matriz_leituras(telemetria)
    bst = construir_bst_balanceada(telemetria)

    alertas = gerar_alertas(telemetria)
    alertas_priorizados = priorizar_alertas(alertas)
    fila_alertas = enfileirar_alertas(alertas)
    pilha_eventos = empilhar_eventos_criticos(log_eventos)
    inconsistencias = detectar_inconsistencias(telemetria)
    tabela_status = classificar_modulos(dicionario_modulos)
    previsao = prever_proximo_ciclo(telemetria)

    return {
        "telemetria": telemetria,
        "log_eventos": log_eventos,
        "dicionario_modulos": dicionario_modulos,
        "hierarquia": hierarquia,
        "matriz": matriz,
        "colunas": colunas,
        "bst": bst,
        "alertas_priorizados": alertas_priorizados,
        "fila_alertas": fila_alertas,
        "pilha_eventos": pilha_eventos,
        "inconsistencias": inconsistencias,
        "tabela_status": tabela_status,
        "previsao": previsao,
    }


def menu():
    """Menu interativo no terminal."""
    contexto = executar_pipeline_completo()

    opcoes = {
        "1": ("Resumo da missao",
              lambda: exibir_resumo_missao(contexto["telemetria"], contexto["dicionario_modulos"])),
        "2": ("Tabela de status dos modulos",
              lambda: exibir_tabela_modulos(contexto["tabela_status"])),
        "3": ("Alertas priorizados",
              lambda: exibir_alertas(contexto["alertas_priorizados"], contexto["fila_alertas"])),
        "4": ("Pilha de eventos criticos",
              lambda: exibir_pilha_eventos(contexto["pilha_eventos"])),
        "5": ("Hierarquia da missao",
              lambda: exibir_hierarquia(contexto["hierarquia"])),
        "6": ("Matriz de leituras",
              lambda: exibir_matriz(contexto["matriz"], contexto["colunas"])),
        "7": ("Previsao (regressao linear)",
              lambda: exibir_previsao(contexto["previsao"])),
        "8": ("Inconsistencias detectadas",
              lambda: exibir_inconsistencias(contexto["inconsistencias"])),
        "9": ("Log completo de eventos",
              lambda: exibir_log_eventos(contexto["log_eventos"])),
        "10": ("Buscar ciclo na BST",
               lambda: _buscar_ciclo_interativo(contexto["bst"])),
        "11": ("Buscar modulo pelo nome",
               lambda: _buscar_modulo_interativo(contexto["dicionario_modulos"])),
        "0": ("Executar TUDO (relatorio completo)",
              lambda: _executar_tudo(contexto)),
    }

    while True:
        cabecalho("SISTEMA DE MONITORAMENTO - AURORA SIGER")
        print("  Selecione uma opcao:")
        print()
        for chave, (rotulo, _) in opcoes.items():
            print(f"    [{chave:>2s}] {rotulo}")
        print(f"    [ q] Sair")
        print()
        escolha = input("  > ").strip().lower()

        if escolha == "q":
            print("  Encerrando.")
            return
        if escolha in opcoes:
            opcoes[escolha][1]()
            input("\n  (enter para voltar ao menu)")
        else:
            print("  Opcao invalida.")


def _executar_tudo(ctx):
    """Imprime todas as analises em sequencia."""
    exibir_resumo_missao(ctx["telemetria"], ctx["dicionario_modulos"])
    exibir_tabela_modulos(ctx["tabela_status"])
    exibir_hierarquia(ctx["hierarquia"])
    exibir_matriz(ctx["matriz"], ctx["colunas"])
    exibir_inconsistencias(ctx["inconsistencias"])
    exibir_log_eventos(ctx["log_eventos"])
    exibir_pilha_eventos(ctx["pilha_eventos"])
    exibir_alertas(ctx["alertas_priorizados"], ctx["fila_alertas"])
    exibir_previsao(ctx["previsao"])


def _buscar_ciclo_interativo(bst):
    """Busca um ciclo especifico na BST (demonstracao de uso da arvore)."""
    try:
        ciclo = int(input("  Ciclo a buscar (1-12): "))
    except ValueError:
        print("  Entrada invalida.")
        return
    resultado = buscar_bst(bst, ciclo)
    if resultado is None:
        print(f"  Ciclo {ciclo} nao encontrado na BST.")
        return
    print(f"\n  Dados do ciclo {ciclo}:")
    for chave, valor in resultado.items():
        print(f"    {chave:<28s} = {valor}")


def _buscar_modulo_interativo(dicionario_modulos):
    """Busca linear por nome de modulo (Fase 2)."""
    print(f"  Modulos disponiveis: {', '.join(MODULOS_CRITICOS)}")
    nome = input("  Nome do modulo: ").strip().lower()
    info = buscar_modulo_por_nome(dicionario_modulos, nome)
    if info is None:
        print(f"  Modulo '{nome}' nao encontrado.")
        return
    print(f"\n  {info['nome']}:")
    print(f"    status atual:    {'ATIVO' if info['status_atual'] == 1 else 'INATIVO'}")
    print(f"    ciclos ativo:    {info['ciclos_ativo']}")
    print(f"    ciclos inativo:  {info['ciclos_inativo']}")
    print(f"    historico:       {info['historico']}")


def main():
    """Ponto de entrada do programa."""
    try:
        menu()
    except KeyboardInterrupt:
        print("\n  Interrompido pelo usuario.")
    except FileNotFoundError as erro:
        print(f"\n  ERRO: arquivo nao encontrado - {erro}")
        print("  Verifique se data/telemetria_missao.csv e data/log_eventos.csv existem.")


if __name__ == "__main__":
    main()
