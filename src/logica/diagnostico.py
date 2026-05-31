"""Classificacao agregada de modulos e deteccao de inconsistencias nos dados."""

from typing import Any

from src.config import CONSUMO_VITAL_MINIMO


def classificar_modulos(dicionario_modulos: dict[str, dict]) -> dict[str, dict[str, Any]]:
    """Classifica cada modulo em NORMAL/ALERTA/CRITICO pelo % de ciclos ativos.

    Criterio:
        >= 90% ativo -> NORMAL
        >= 50% ativo -> ALERTA
        <  50% ativo -> CRITICO
    """
    tabela: dict[str, dict[str, Any]] = {}
    for nome, dados in dicionario_modulos.items():
        total = len(dados["historico"])
        pct_ativo = (dados["ciclos_ativo"] / total) * 100 if total > 0 else 0.0

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


def detectar_inconsistencias(telemetria: list[dict]) -> list[dict[str, Any]]:
    """Identifica leituras conflitantes nos dados (requisito do paper §7).

    Detecta:
        - comunicacao=1 mas qualidade_comunicacao_pct=0 (sensor conflitante)
        - energia=1 mas reserva_energia_pct=0 (falha de leitura)
        - suporte_vida=1 mas consumo < minimo vital (anomalia)
    """
    inconsistencias: list[dict[str, Any]] = []
    for registro in telemetria:
        inconsistencias.extend(_inspecionar_registro(registro))
    return inconsistencias


def _inspecionar_registro(registro: dict) -> list[dict[str, Any]]:
    """Aplica todas as regras de inconsistencia a um registro."""
    achados: list[dict[str, Any]] = []
    ciclo = registro["ciclo"]

    if registro["comunicacao"] == 1 and registro["qualidade_comunicacao_pct"] == 0:
        achados.append({
            "ciclo": ciclo,
            "tipo": "SENSOR_CONFLITANTE",
            "descricao": "Modulo comunicacao=1 mas qualidade=0 (sensor reportando dados conflitantes)",
        })

    if registro["energia"] == 1 and registro["reserva_energia_pct"] == 0:
        achados.append({
            "ciclo": ciclo,
            "tipo": "SENSOR_CONFLITANTE",
            "descricao": "Modulo energia=1 mas reserva=0 (falha de leitura)",
        })

    if registro["suporte_vida"] == 1 and registro["consumo_total_kwh"] < CONSUMO_VITAL_MINIMO:
        achados.append({
            "ciclo": ciclo,
            "tipo": "CONSUMO_SUSPEITO",
            "descricao": f"Suporte a vida ativo com consumo total < {CONSUMO_VITAL_MINIMO} kWh (anomalia)",
        })

    return achados
