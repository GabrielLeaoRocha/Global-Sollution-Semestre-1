"""Fila FIFO de alertas pendentes.

Adaptada de FilaPouso (Fase 2 — mgpeb-aurora-siger/src/estruturas.py).
Primeiro alerta gerado e o primeiro a ser processado pelo operador.
"""

from typing import Any


class FilaAlertas:
    """Fila FIFO simples implementada sobre uma lista Python.

    Operacoes (todas O(1) amortizado, exceto dequeue que e O(n)):
        enqueue  — adiciona ao final
        dequeue  — remove e retorna o primeiro
        front    — retorna o primeiro sem remover
        is_empty — verifica se esta vazia
        size     — retorna a quantidade de elementos
        listar   — retorna copia da fila
    """

    def __init__(self) -> None:
        self._fila: list[Any] = []

    def enqueue(self, alerta: Any) -> None:
        """Adiciona alerta no final da fila."""
        self._fila.append(alerta)

    def dequeue(self) -> Any | None:
        """Remove e retorna o alerta mais antigo, ou None se vazia."""
        if self.is_empty():
            return None
        return self._fila.pop(0)

    def front(self) -> Any | None:
        """Retorna o proximo alerta sem remover, ou None se vazia."""
        if self.is_empty():
            return None
        return self._fila[0]

    def is_empty(self) -> bool:
        return len(self._fila) == 0

    def size(self) -> int:
        return len(self._fila)

    def listar(self) -> list[Any]:
        """Copia rasa da fila (ordem FIFO)."""
        return list(self._fila)

    def __repr__(self) -> str:
        return f"FilaAlertas(size={self.size()})"
