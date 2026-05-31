"""Geracao, priorizacao e armazenamento de alertas em estruturas FIFO/LIFO."""

from typing import Any

from src.config import SEV_ALERTA
from src.estruturas import FilaAlertas, PilhaEventos, ordenar_alertas_por_severidade
from src.logica.regras import avaliar_ciclo


def gerar_alertas(telemetria: list[dict]) -> list[dict[str, Any]]:
    """Gera alertas para cada ciclo aplicando as regras logicas.

    Returns:
        Lista contendo apenas alertas com severidade ALERTA ou CRITICO.
    """
    return [
        avaliacao
        for registro in telemetria
        if (avaliacao := avaliar_ciclo(registro))["severidade_num"] <= SEV_ALERTA
    ]


def priorizar_alertas(lista_alertas: list[dict]) -> list[dict[str, Any]]:
    """Ordena alertas por severidade usando bubble sort (Fase 2)."""
    return ordenar_alertas_por_severidade(lista_alertas)


def enfileirar_alertas(lista_alertas: list[dict]) -> FilaAlertas:
    """Insere alertas em uma FilaAlertas (FIFO, ordem de chegada)."""
    fila = FilaAlertas()
    for alerta in lista_alertas:
        fila.enqueue(alerta)
    return fila


def empilhar_eventos_criticos(log_eventos: list[dict]) -> PilhaEventos:
    """Empilha eventos com severidade CRITICO em uma PilhaEventos (LIFO)."""
    pilha = PilhaEventos()
    for evento in log_eventos:
        if evento["severidade"] == "CRITICO":
            pilha.push(evento)
    return pilha
