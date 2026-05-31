"""Algoritmos de busca e ordenacao.

Origem: Fase 2 (busca linear + bubble sort em estruturas.py).
"""

from typing import Any


def buscar_modulo_por_nome(dicionario_modulos: dict, nome: str) -> dict | None:
    """Busca linear por chave em um dicionario, O(n).

    Embora o acesso direto a um dicionario seja O(1), a busca linear
    e mantida aqui para demonstrar o algoritmo da Fase 2.

    Args:
        dicionario_modulos: hash com nome -> dados do modulo.
        nome: chave a buscar.

    Returns:
        Dados do modulo ou None se nao encontrado.
    """
    for chave, valor in dicionario_modulos.items():
        if chave == nome:
            return valor
    return None


def ordenar_alertas_por_severidade(lista_alertas: list[dict]) -> list[dict]:
    """Bubble sort O(n^2) para ordenacao de alertas por severidade.

    Estavel e simples — adequado para volume tipico de alertas (< 50)
    em uma missao espacial. Mantido para demonstrar o algoritmo
    da Fase 2 (ordenar_por_prioridade).

    Otimizacao: early-exit quando nao ha trocas em uma passada completa.

    Args:
        lista_alertas: cada alerta precisa ter a chave 'severidade_num'.

    Returns:
        Nova lista ordenada (severidade_num crescente; menor = mais critico).
    """
    copia = list(lista_alertas)
    n = len(copia)
    for i in range(n):
        trocou = False
        for j in range(0, n - i - 1):
            if copia[j]["severidade_num"] > copia[j + 1]["severidade_num"]:
                copia[j], copia[j + 1] = copia[j + 1], copia[j]
                trocou = True
        if not trocou:
            break
    return copia
