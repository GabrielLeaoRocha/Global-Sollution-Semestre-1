"""Pacote de leitura e organizacao de dados — Fase 3 (data_loader.py).

Re-exporta a API publica.
"""

from src.dados.loader import carregar_csv, carregar_log_eventos, carregar_telemetria
from src.dados.organizacao import (
    construir_dicionario_modulos,
    construir_hierarquia,
    construir_matriz_leituras,
)

__all__ = [
    "carregar_csv",
    "carregar_log_eventos",
    "carregar_telemetria",
    "construir_dicionario_modulos",
    "construir_hierarquia",
    "construir_matriz_leituras",
]
