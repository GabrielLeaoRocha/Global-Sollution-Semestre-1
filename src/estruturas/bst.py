"""Binary Search Tree (BST) indexada por ciclo de telemetria.

Reutilizada de binary_tree.py (Fase 3 — aurora-core/src/binary_tree.py).
Permite busca eficiente O(log n) por ciclo em uma serie temporal.
"""

from typing import Any


class NoBST:
    """No da arvore binaria de busca indexada por ciclo."""

    __slots__ = ("ciclo", "dados", "esquerda", "direita")

    def __init__(self, ciclo: int, dados: dict) -> None:
        self.ciclo: int = ciclo
        self.dados: dict = dados
        self.esquerda: NoBST | None = None
        self.direita: NoBST | None = None


def inserir_bst(raiz: NoBST | None, ciclo: int, dados: dict) -> NoBST:
    """Insere uma leitura na BST recursivamente.

    Args:
        raiz: No raiz da arvore (ou subarvore).
        ciclo: Chave de busca.
        dados: Dicionario associado aquele ciclo.

    Returns:
        Raiz atualizada (necessario para encadeamento recursivo).
    """
    if raiz is None:
        return NoBST(ciclo, dados)
    if ciclo < raiz.ciclo:
        raiz.esquerda = inserir_bst(raiz.esquerda, ciclo, dados)
    elif ciclo > raiz.ciclo:
        raiz.direita = inserir_bst(raiz.direita, ciclo, dados)
    else:
        raiz.dados = dados
    return raiz


def buscar_bst(raiz: NoBST | None, ciclo: int) -> dict | None:
    """Busca os dados de um ciclo na BST, O(log n) em arvore balanceada.

    Returns:
        Dicionario do ciclo ou None se nao encontrado.
    """
    if raiz is None:
        return None
    if ciclo == raiz.ciclo:
        return raiz.dados
    if ciclo < raiz.ciclo:
        return buscar_bst(raiz.esquerda, ciclo)
    return buscar_bst(raiz.direita, ciclo)


def construir_bst_balanceada(leituras: list[dict]) -> NoBST | None:
    """Constroi BST balanceada ordenando e inserindo pelo elemento mediano."""
    if not leituras:
        return None
    ordenadas = sorted(leituras, key=lambda r: r["ciclo"])
    return _construir_balanceada(ordenadas, 0, len(ordenadas) - 1)


def _construir_balanceada(lista: list[dict], ini: int, fim: int) -> NoBST | None:
    """Recursao helper: divide a lista pela mediana para balancear a arvore."""
    if ini > fim:
        return None
    meio = (ini + fim) // 2
    no = NoBST(lista[meio]["ciclo"], lista[meio])
    no.esquerda = _construir_balanceada(lista, ini, meio - 1)
    no.direita = _construir_balanceada(lista, meio + 1, fim)
    return no


def percorrer_em_ordem(raiz: NoBST | None) -> list[tuple[int, dict]]:
    """Percorre a BST em ordem crescente de ciclo (in-order traversal)."""
    if raiz is None:
        return []
    return (
        percorrer_em_ordem(raiz.esquerda)
        + [(raiz.ciclo, raiz.dados)]
        + percorrer_em_ordem(raiz.direita)
    )
