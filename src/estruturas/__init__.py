"""Pacote de estruturas de dados — Fase 2 (fila, pilha, busca, ordenacao)
e Fase 3 (BST).

Re-exporta a API publica para uso pelo restante do sistema.
"""

from src.estruturas.fila import FilaAlertas
from src.estruturas.pilha import PilhaEventos
from src.estruturas.bst import NoBST, buscar_bst, construir_bst_balanceada, inserir_bst
from src.estruturas.algoritmos import buscar_modulo_por_nome, ordenar_alertas_por_severidade

__all__ = [
    "FilaAlertas",
    "PilhaEventos",
    "NoBST",
    "buscar_bst",
    "construir_bst_balanceada",
    "inserir_bst",
    "buscar_modulo_por_nome",
    "ordenar_alertas_por_severidade",
]
