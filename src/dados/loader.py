"""Leitura de CSVs de telemetria e log de eventos.

Adaptado de load_csv() (Fase 3 — aurora-core/src/data_loader.py).
"""

import csv
import os
from typing import Any


# Raiz do projeto = pai do diretorio src/
_RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DIR_DADOS = os.path.join(_RAIZ_PROJETO, "data")


def carregar_csv(caminho: str) -> list[dict[str, Any]]:
    """Le um arquivo CSV e retorna lista de dicionarios com tipos convertidos.

    Conversao automatica por coluna:
      - inteiro (string sem ponto decimal)
      - float (string com ponto decimal)
      - string (fallback)

    Args:
        caminho: caminho absoluto ou relativo do arquivo CSV.

    Returns:
        Lista de dicionarios — cada linha vira um dict {coluna: valor}.

    Raises:
        FileNotFoundError: se o arquivo nao existir.
    """
    registros: list[dict[str, Any]] = []
    with open(caminho, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            convertida: dict[str, Any] = {}
            for chave, valor in linha.items():
                convertida[chave] = _converter_valor(valor)
            registros.append(convertida)
    return registros


def _converter_valor(valor: str) -> Any:
    """Converte uma string CSV para int, float ou mantem como string."""
    try:
        return int(valor) if "." not in valor else float(valor)
    except ValueError:
        return valor


def carregar_telemetria() -> list[dict[str, Any]]:
    """Carrega data/telemetria_missao.csv a partir da raiz do projeto."""
    return carregar_csv(os.path.join(_DIR_DADOS, "telemetria_missao.csv"))


def carregar_log_eventos() -> list[dict[str, Any]]:
    """Carrega data/log_eventos.csv a partir da raiz do projeto."""
    return carregar_csv(os.path.join(_DIR_DADOS, "log_eventos.csv"))
