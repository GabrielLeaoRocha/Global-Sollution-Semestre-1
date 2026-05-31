"""Regressao linear simples pelo metodo dos minimos quadrados.

Reutilizada de regression_model.py (Fase 3 — aurora-core/src/regression_model.py).
Implementacao manual, sem bibliotecas externas.
"""

from typing import Any

from src.config import RESERVA_ALERTA, RESERVA_CRITICA


def media(valores: list[float]) -> float:
    """Media aritmetica de uma lista de numeros."""
    return sum(valores) / len(valores)


def regressao_linear(x_vals: list[float], y_vals: list[float]) -> tuple[float, float]:
    """Calcula coeficientes (beta_0, beta_1) da regressao linear simples.

    Formulas (minimos quadrados):
        beta_1 = SUM[(x - x_med)(y - y_med)] / SUM[(x - x_med)^2]
        beta_0 = y_med - beta_1 * x_med

    Returns:
        Tupla (intercepto, coeficiente_angular).
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


def prever(x: float, beta_0: float, beta_1: float) -> float:
    """Previsao do modelo linear: y = beta_0 + beta_1 * x."""
    return beta_0 + beta_1 * x


def r_quadrado(
    x_vals: list[float], y_vals: list[float], beta_0: float, beta_1: float
) -> float:
    """Coeficiente de determinacao R^2 (qualidade do ajuste, 0 a 1)."""
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


def prever_proximo_ciclo(telemetria: list[dict]) -> dict[str, Any]:
    """Aplica regressao linear sobre reserva_energia_pct para prever proximo ciclo.

    A previsao influencia recomendacao automatica (paper §8.5):
        ŷ < 20% -> alerta preventivo CRITICO
        ŷ < 50% -> alerta preventivo ALERTA
        caso contrario -> operacao normal

    Returns:
        Dict com beta_0, beta_1, r_quadrado, proximo_ciclo, reserva_prevista_pct,
        recomendacao e nivel.
    """
    x_vals = [r["ciclo"] for r in telemetria]
    y_vals = [r["reserva_energia_pct"] for r in telemetria]

    beta_0, beta_1 = regressao_linear(x_vals, y_vals)
    r2 = r_quadrado(x_vals, y_vals, beta_0, beta_1)

    proximo_ciclo = x_vals[-1] + 1
    reserva_prevista = prever(proximo_ciclo, beta_0, beta_1)

    nivel, recomendacao = _classificar_previsao(reserva_prevista)

    return {
        "beta_0": round(beta_0, 4),
        "beta_1": round(beta_1, 4),
        "r_quadrado": round(r2, 4),
        "proximo_ciclo": proximo_ciclo,
        "reserva_prevista_pct": round(reserva_prevista, 2),
        "recomendacao": recomendacao,
        "nivel": nivel,
    }


def _classificar_previsao(reserva_prevista: float) -> tuple[str, str]:
    """Define nivel e recomendacao com base na reserva projetada."""
    if reserva_prevista < RESERVA_CRITICA:
        return (
            "CRITICO",
            "PREVENTIVO CRITICO: reserva projetada abaixo de 20%. "
            "Acionar protocolo de emergencia ANTES do proximo ciclo.",
        )
    if reserva_prevista < RESERVA_ALERTA:
        return (
            "ALERTA",
            "PREVENTIVO ALERTA: reserva projetada abaixo de 50%. "
            "Desligar sistemas nao essenciais preventivamente.",
        )
    return ("NORMAL", "Reserva projetada dentro da faixa segura.")
