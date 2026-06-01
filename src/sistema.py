"""Sistema Inteligente de Monitoramento — Missao Aurora Siger.

Global Solution — FIAP Engenharia de Software 1ESPR
RM 571330 — Gabriel de Leao Rocha

Entrypoint do sistema. Orquestra os pacotes modulares e expoe o menu
interativo no terminal.

Arquitetura:
    src/
    ├── config.py         constantes (faixas seguras, severidades)
    ├── estruturas/       fila, pilha, BST, busca/ordenacao (Fase 2 + 3)
    ├── dados/            leitura de CSV, organizacao em dict/hierarquia/matriz
    ├── logica/           regras AND/OR/NOT, alertas, diagnostico
    ├── previsao/         regressao linear (Fase 3)
    └── exibicao/         apresentacao no terminal

Execucao:
    python3 -m src.sistema
"""

import os
import sys
from typing import Any, Callable

# Garante que a raiz do projeto esteja no PYTHONPATH quando executado como
# `python3 src/sistema.py` (sem o flag -m). Necessario para os imports
# absolutos `from src.X` funcionarem dos dois modos.
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from src.config import MODULOS_CRITICOS
from src.dados import (
    carregar_log_eventos,
    carregar_telemetria,
    construir_dicionario_modulos,
    construir_hierarquia,
    construir_matriz_leituras,
)
from src.estruturas import (
    FilaAlertas,
    PilhaEventos,
    buscar_bst,
    buscar_modulo_por_nome,
    construir_bst_balanceada,
)
from src.exibicao import (
    cabecalho,
    exibir_alertas,
    exibir_hierarquia,
    exibir_inconsistencias,
    exibir_log_eventos,
    exibir_matriz,
    exibir_pilha_eventos,
    exibir_previsao,
    exibir_resumo_missao,
    exibir_tabela_modulos,
)
from src.logica import (
    classificar_modulos,
    detectar_inconsistencias,
    empilhar_eventos_criticos,
    enfileirar_alertas,
    gerar_alertas,
    priorizar_alertas,
)
from src.previsao import prever_proximo_ciclo


# =============================================================================
# PIPELINE
# =============================================================================

def executar_pipeline() -> dict[str, Any]:
    """Carrega dados, monta estruturas e calcula todas as analises.

    Returns:
        Contexto consolidado com todas as estruturas e resultados,
        usado tanto pelo menu interativo quanto por execucoes em modo batch.
    """
    telemetria = carregar_telemetria()
    log_eventos = carregar_log_eventos()

    return {
        "telemetria": telemetria,
        "log_eventos": log_eventos,
        "dicionario_modulos": construir_dicionario_modulos(telemetria),
        "hierarquia": construir_hierarquia(telemetria),
        "matriz_e_colunas": construir_matriz_leituras(telemetria),
        "bst": construir_bst_balanceada(telemetria),
        "alertas": gerar_alertas(telemetria),
        "pilha_eventos": empilhar_eventos_criticos(log_eventos),
        "inconsistencias": detectar_inconsistencias(telemetria),
        "previsao": prever_proximo_ciclo(telemetria),
    }


def consolidar_alertas(ctx: dict[str, Any]) -> tuple[list[dict], FilaAlertas]:
    """Prioriza e enfileira os alertas a partir do contexto."""
    priorizados = priorizar_alertas(ctx["alertas"])
    fila = enfileirar_alertas(ctx["alertas"])
    return priorizados, fila


# =============================================================================
# MENU INTERATIVO
# =============================================================================

def _construir_opcoes(ctx: dict[str, Any]) -> dict[str, tuple[str, Callable[[], None]]]:
    """Monta o dicionario de opcoes do menu (chave -> (rotulo, acao))."""
    matriz, colunas = ctx["matriz_e_colunas"]
    tabela_status = classificar_modulos(ctx["dicionario_modulos"])
    alertas_priorizados, fila_alertas = consolidar_alertas(ctx)

    return {
        "1": ("Resumo da missao",
              lambda: exibir_resumo_missao(ctx["telemetria"], ctx["dicionario_modulos"])),
        "2": ("Tabela de status dos modulos",
              lambda: exibir_tabela_modulos(tabela_status)),
        "3": ("Alertas priorizados",
              lambda: exibir_alertas(alertas_priorizados, fila_alertas)),
        "4": ("Pilha de eventos criticos",
              lambda: exibir_pilha_eventos(ctx["pilha_eventos"])),
        "5": ("Hierarquia da missao",
              lambda: exibir_hierarquia(ctx["hierarquia"])),
        "6": ("Matriz de leituras",
              lambda: exibir_matriz(matriz, colunas)),
        "7": ("Previsao (regressao linear)",
              lambda: exibir_previsao(ctx["previsao"])),
        "8": ("Inconsistencias detectadas",
              lambda: exibir_inconsistencias(ctx["inconsistencias"])),
        "9": ("Log completo de eventos",
              lambda: exibir_log_eventos(ctx["log_eventos"])),
        "10": ("Buscar ciclo na BST",
               lambda: _buscar_ciclo_interativo(ctx["bst"])),
        "11": ("Buscar modulo pelo nome",
               lambda: _buscar_modulo_interativo(ctx["dicionario_modulos"])),
        "0": ("Executar TUDO (relatorio completo)",
              lambda: _executar_tudo(ctx, tabela_status, alertas_priorizados, fila_alertas)),
    }


def menu() -> None:
    """Loop principal do menu interativo."""
    ctx = executar_pipeline()
    opcoes = _construir_opcoes(ctx)

    while True:
        cabecalho("SISTEMA DE MONITORAMENTO - AURORA SIGER")
        print("  Selecione uma opcao:")
        print()
        for chave, (rotulo, _) in opcoes.items():
            print(f"    [{chave:>2s}] {rotulo}")
        print(f"    [ g] Abrir interface grafica (tkinter)")
        print(f"    [ q] Sair")
        print()
        escolha = input("  > ").strip().lower()

        if escolha == "q":
            print("  Encerrando.")
            return
        if escolha == "g":
            _abrir_interface_grafica()
            continue
        if escolha in opcoes:
            opcoes[escolha][1]()
            input("\n  (enter para voltar ao menu)")
        else:
            print("  Opcao invalida.")


def _abrir_interface_grafica() -> None:
    """Lanca a GUI tkinter (bloqueia ate a janela ser fechada)."""
    try:
        from src.interface_grafica import main as gui_main
        gui_main()
    except ImportError as erro:
        print(f"  ERRO: nao foi possivel carregar a interface grafica - {erro}")
    except Exception as erro:
        print(f"  ERRO ao abrir a interface grafica: {erro}")


def _executar_tudo(
    ctx: dict[str, Any],
    tabela_status: dict,
    alertas_priorizados: list[dict],
    fila_alertas: FilaAlertas,
) -> None:
    """Imprime todas as analises em sequencia (modo relatorio)."""
    matriz, colunas = ctx["matriz_e_colunas"]
    exibir_resumo_missao(ctx["telemetria"], ctx["dicionario_modulos"])
    exibir_tabela_modulos(tabela_status)
    exibir_hierarquia(ctx["hierarquia"])
    exibir_matriz(matriz, colunas)
    exibir_inconsistencias(ctx["inconsistencias"])
    exibir_log_eventos(ctx["log_eventos"])
    exibir_pilha_eventos(ctx["pilha_eventos"])
    exibir_alertas(alertas_priorizados, fila_alertas)
    exibir_previsao(ctx["previsao"])


def _buscar_ciclo_interativo(bst) -> None:
    """Demonstracao da busca O(log n) na BST."""
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


def _buscar_modulo_interativo(dicionario_modulos: dict) -> None:
    """Demonstracao da busca linear (Fase 2) por nome de modulo."""
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


# =============================================================================
# ENTRYPOINT
# =============================================================================

def main() -> int:
    """Ponto de entrada do programa.

    Returns:
        Codigo de saida (0 = sucesso, 1 = erro de I/O).
    """
    try:
        menu()
        return 0
    except KeyboardInterrupt:
        print("\n  Interrompido pelo usuario.")
        return 0
    except FileNotFoundError as erro:
        print(f"\n  ERRO: arquivo nao encontrado - {erro}")
        print("  Verifique se data/telemetria_missao.csv e data/log_eventos.csv existem.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
