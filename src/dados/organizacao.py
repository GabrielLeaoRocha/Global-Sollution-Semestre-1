"""Organiza a telemetria nas estruturas exigidas (dicionario, hierarquia, matriz).

Adaptado de build_colony_structure() (Fase 3 — aurora-core/src/data_loader.py).
"""

from typing import Any

from src.config import COLUNAS_NUMERICAS, MODULOS_CRITICOS


def construir_dicionario_modulos(telemetria: list[dict]) -> dict[str, dict[str, Any]]:
    """Dicionario/hash com acesso O(1) ao status agregado de cada modulo.

    Para cada modulo critico, calcula:
        - historico: lista de status (0/1) por ciclo
        - status_atual: ultimo valor do historico
        - ciclos_ativo / ciclos_inativo: contagens absolutas

    Args:
        telemetria: lista de registros (um por ciclo).

    Returns:
        Dict {nome_modulo: dados_agregados}.
    """
    modulos: dict[str, dict[str, Any]] = {}
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


def construir_hierarquia(telemetria: list[dict]) -> dict[str, Any]:
    """Hierarquia da missao (3 niveis): missao -> sistemas -> subsistemas.

    Adaptada de build_colony_structure() — agrupa os 6 modulos do paper
    em 3 sistemas logicos (energia, habitat, operacional).
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


def construir_matriz_leituras(
    telemetria: list[dict],
) -> tuple[list[list[float]], list[str]]:
    """Matriz (lista de listas) [ciclo][variavel].

    Returns:
        (matriz, colunas) onde matriz[i][j] e o valor da j-esima variavel
        no i-esimo ciclo, e colunas e a lista de nomes das variaveis.
    """
    matriz = [[registro[coluna] for coluna in COLUNAS_NUMERICAS] for registro in telemetria]
    return matriz, list(COLUNAS_NUMERICAS)
