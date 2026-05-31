"""Pilha LIFO dos ultimos eventos criticos analisados.

Reutilizada de PilhaHistorico (Fase 2 — mgpeb-aurora-siger/src/estruturas.py).
Ultimo evento empilhado e o primeiro consultado.
"""

from typing import Any


class PilhaEventos:
    """Pilha LIFO simples implementada sobre uma lista Python.

    Operacoes (todas O(1)):
        push     — empilha um novo evento
        pop      — remove e retorna o topo
        peek     — retorna o topo sem remover
        is_empty — verifica se esta vazia
        size     — retorna a quantidade de elementos
        listar   — retorna copia (topo primeiro)
    """

    def __init__(self) -> None:
        self._pilha: list[Any] = []

    def push(self, evento: Any) -> None:
        """Empilha um novo evento no topo."""
        self._pilha.append(evento)

    def pop(self) -> Any | None:
        """Remove e retorna o evento do topo, ou None se vazia."""
        if self.is_empty():
            return None
        return self._pilha.pop()

    def peek(self) -> Any | None:
        """Retorna o evento do topo sem remover, ou None se vazia."""
        if self.is_empty():
            return None
        return self._pilha[-1]

    def is_empty(self) -> bool:
        return len(self._pilha) == 0

    def size(self) -> int:
        return len(self._pilha)

    def listar(self) -> list[Any]:
        """Copia da pilha com o topo (mais recente) primeiro."""
        return list(reversed(self._pilha))

    def __repr__(self) -> str:
        return f"PilhaEventos(size={self.size()})"
