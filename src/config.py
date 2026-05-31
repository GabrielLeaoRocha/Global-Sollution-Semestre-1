"""Constantes e faixas de seguranca do sistema.

Origem: Fase 1 (faixas-seguras.md) — limiares operacionais de telemetria.
"""

from typing import Final

# ---------------------------------------------------------------------------
# FAIXAS DE SEGURANCA — RESERVA ENERGETICA (%)
# ---------------------------------------------------------------------------
RESERVA_CRITICA: Final[float] = 20.0
RESERVA_ALERTA: Final[float] = 50.0

# ---------------------------------------------------------------------------
# FAIXAS DE SEGURANCA — RADIACAO (escala 0-100)
# ---------------------------------------------------------------------------
RADIACAO_CRITICA: Final[float] = 80.0
RADIACAO_ALERTA: Final[float] = 60.0

# ---------------------------------------------------------------------------
# FAIXAS DE SEGURANCA — COMUNICACAO (%)
# ---------------------------------------------------------------------------
COMUNICACAO_CRITICA: Final[float] = 30.0
COMUNICACAO_ALERTA: Final[float] = 70.0

# ---------------------------------------------------------------------------
# FAIXAS DE SEGURANCA — TEMPERATURA EXTERNA (Celsius, ambiente marciano)
# ---------------------------------------------------------------------------
TEMPERATURA_MIN_SEGURA: Final[float] = -70.0

# ---------------------------------------------------------------------------
# CONSUMO VITAL MINIMO (kWh) — abaixo disso, suporte_vida=1 e suspeito
# ---------------------------------------------------------------------------
CONSUMO_VITAL_MINIMO: Final[float] = 10.0

# ---------------------------------------------------------------------------
# SEVERIDADES — menor numero = mais urgente (para ordenacao crescente)
# ---------------------------------------------------------------------------
SEV_CRITICO: Final[int] = 1
SEV_ALERTA: Final[int] = 2
SEV_NORMAL: Final[int] = 3

# ---------------------------------------------------------------------------
# MODULOS CRITICOS DA MISSAO (paper §7 — minimo 6 modulos binarios)
# ---------------------------------------------------------------------------
MODULOS_CRITICOS: Final[list[str]] = [
    "suporte_vida",
    "energia",
    "comunicacao",
    "habitat",
    "laboratorio",
    "armazenamento",
]

# ---------------------------------------------------------------------------
# COLUNAS NUMERICAS DA TELEMETRIA (usadas pela matriz de leituras)
# ---------------------------------------------------------------------------
COLUNAS_NUMERICAS: Final[list[str]] = [
    "geracao_solar_kwh",
    "geracao_eolica_kwh",
    "consumo_total_kwh",
    "reserva_energia_pct",
    "temperatura_externa_c",
    "radiacao_nivel",
    "qualidade_comunicacao_pct",
    "velocidade_vento_ms",
]
