"""Pacote de logica de negocio — regras, alertas e diagnostico."""

from src.logica.alertas import (
    empilhar_eventos_criticos,
    enfileirar_alertas,
    gerar_alertas,
    priorizar_alertas,
)
from src.logica.diagnostico import classificar_modulos, detectar_inconsistencias
from src.logica.regras import avaliar_ciclo

__all__ = [
    "avaliar_ciclo",
    "classificar_modulos",
    "detectar_inconsistencias",
    "empilhar_eventos_criticos",
    "enfileirar_alertas",
    "gerar_alertas",
    "priorizar_alertas",
]
