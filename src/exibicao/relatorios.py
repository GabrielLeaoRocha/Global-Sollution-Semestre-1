"""Funcoes de apresentacao no terminal — cabecalho, tabelas e relatorios."""

from typing import Any

from src.config import MODULOS_CRITICOS
from src.estruturas import FilaAlertas, PilhaEventos
from src.previsao import media

_LARGURA_LINHA = 70


def cabecalho(titulo: str) -> None:
    """Imprime cabecalho formatado com titulo destacado."""
    print()
    print("=" * _LARGURA_LINHA)
    print(f"  {titulo}")
    print("=" * _LARGURA_LINHA)


def exibir_resumo_missao(telemetria: list[dict], dicionario_modulos: dict) -> None:
    """Resumo geral da missao no ultimo ciclo + medias agregadas."""
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


def exibir_tabela_modulos(tabela_status: dict[str, dict[str, Any]]) -> None:
    """Tabela com classificacao de cada modulo (% ciclos ativos)."""
    cabecalho("TABELA DE STATUS DOS MODULOS (% ciclos ativos)")
    print(f"  {'MODULO':<18s} {'STATUS':<10s} {'% ATIVO':<10s} {'ATUAL':<8s}")
    print(f"  {'-' * 18} {'-' * 10} {'-' * 10} {'-' * 8}")
    for nome, info in tabela_status.items():
        atual = "1" if info["status_atual"] == 1 else "0"
        print(f"  {nome:<18s} {info['status']:<10s} {info['pct_ativo']:<10.1f} {atual:<8s}")


def exibir_alertas(
    alertas_priorizados: list[dict], fila_alertas: FilaAlertas
) -> None:
    """Lista alertas em ordem de severidade (mais critico primeiro)."""
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

    proximo = fila_alertas.front()
    if proximo is not None:
        print(f"  Fila FIFO (proximo a processar): ciclo {proximo['ciclo']}")
        print(f"  Total na fila: {fila_alertas.size()}")


def exibir_pilha_eventos(pilha_eventos: PilhaEventos) -> None:
    """Lista eventos criticos em ordem LIFO (topo = mais recente)."""
    cabecalho(f"PILHA DE EVENTOS CRITICOS ({pilha_eventos.size()} eventos)")
    if pilha_eventos.is_empty():
        print("  Nenhum evento critico empilhado.")
        return
    for i, evento in enumerate(pilha_eventos.listar(), 1):
        marca = "TOPO ->" if i == 1 else "       "
        print(f"  {marca} ciclo {evento['ciclo']:>2d} | {evento['modulo']:<14s} | {evento['descricao']}")


def exibir_hierarquia(hierarquia: dict[str, Any]) -> None:
    """Renderiza a hierarquia missao -> sistemas -> subsistemas em ASCII tree."""
    cabecalho("HIERARQUIA DA MISSAO")
    print(f"  {hierarquia['missao']}")
    for sistema, conteudo in hierarquia["sistemas"].items():
        print(f"    |- {sistema}")
        for subsistema in conteudo.keys():
            print(f"    |    |- {subsistema}")


def exibir_matriz(matriz: list[list[float]], colunas: list[str]) -> None:
    """Tabela formatada da matriz de leituras (ciclo x variavel)."""
    cabecalho("MATRIZ DE LEITURAS (ciclo x variavel)")
    cabecalhos = ["CICLO"] + [c[:12] for c in colunas]
    print("  " + " ".join(f"{h:>13s}" for h in cabecalhos))
    print("  " + "-" * (14 * len(cabecalhos)))
    for i, linha in enumerate(matriz, 1):
        valores = [f"{i:>13d}"] + [f"{v:>13.2f}" for v in linha]
        print("  " + " ".join(valores))


def exibir_previsao(previsao: dict[str, Any]) -> None:
    """Resultado da regressao linear + recomendacao automatica."""
    cabecalho("PREVISAO - REGRESSAO LINEAR (reserva energetica)")
    print(f"  Modelo:                  y = {previsao['beta_0']:.4f} + {previsao['beta_1']:.4f} * x")
    print(f"  R^2 (qualidade do ajuste): {previsao['r_quadrado']:.4f}")
    print(f"  Proximo ciclo:           {previsao['proximo_ciclo']}")
    print(f"  Reserva prevista:        {previsao['reserva_prevista_pct']:.2f}%")
    print(f"  Nivel:                   {previsao['nivel']}")
    print(f"  Recomendacao:")
    print(f"    >> {previsao['recomendacao']}")


def exibir_inconsistencias(inconsistencias: list[dict[str, Any]]) -> None:
    """Lista todas as inconsistencias detectadas nos dados."""
    cabecalho(f"INCONSISTENCIAS DETECTADAS ({len(inconsistencias)})")
    if not inconsistencias:
        print("  Nenhuma inconsistencia detectada.")
        return
    for inc in inconsistencias:
        print(f"  ciclo {inc['ciclo']:>2d} | {inc['tipo']:<22s} | {inc['descricao']}")


def exibir_log_eventos(log_eventos: list[dict]) -> None:
    """Log completo de eventos como tabela."""
    cabecalho(f"LOG DE EVENTOS ({len(log_eventos)} registros)")
    print(f"  {'ID':<4s} {'CICLO':<6s} {'TIPO':<22s} {'MODULO':<14s} {'SEV':<10s}")
    print("  " + "-" * 66)
    for ev in log_eventos:
        print(
            f"  {str(ev['id']):<4s} {str(ev['ciclo']):<6s} "
            f"{ev['tipo']:<22s} {ev['modulo']:<14s} {ev['severidade']:<10s}"
        )
