"""Memoria de trabajo — buffer circular de las últimas N interacciones.

Como la memoria a corto plazo humana: mantiene el contexto inmediato
de la conversación, descartando lo más antiguo automáticamente.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from collections import deque
from typing import Optional

from franquenstein.config import WORKING_MEMORY_SIZE


@dataclass
class WorkingMemoryItem:
    """Un elemento en la memoria de trabajo."""

    input_text: str
    output_text: str = ""
    emotion: str = "neutral"
    timestamp: float = field(default_factory=time.time)


class WorkingMemory:
    """Buffer circular que mantiene las últimas N interacciones.

    Es rápida y efímera — vive solo en RAM.
    Se usa para dar contexto inmediato al razonamiento.
    """

    def __init__(self, capacity: int = WORKING_MEMORY_SIZE):
        self._capacity = capacity
        self._buffer: deque[WorkingMemoryItem] = deque(maxlen=capacity)

    # ─── API pública ─────────────────────────────────────────

    def push(self, item: WorkingMemoryItem) -> None:
        """Añade una interacción al buffer (la más antigua se descarta si está lleno)."""
        self._buffer.append(item)

    def get_recent(self, n: Optional[int] = None) -> list[WorkingMemoryItem]:
        """Devuelve las últimas n interacciones (o todas si n=None)."""
        items = list(self._buffer)
        if n is not None:
            items = items[-n:]
        return items

    def get_context_string(self) -> str:
        """Genera un string con el contexto reciente para alimentar al razonamiento."""
        if not self._buffer:
            return "(sin contexto previo)"

        lines: list[str] = []
        for item in self._buffer:
            lines.append(f"[Usuario]: {item.input_text}")
            if item.output_text:
                lines.append(f"[Franquenstein]: {item.output_text}")
        return "\n".join(lines)

    def search(self, query: str) -> list[WorkingMemoryItem]:
        """Busca en la memoria de trabajo por coincidencia simple."""
        query_lower = query.lower()
        return [
            item
            for item in self._buffer
            if query_lower in item.input_text.lower()
            or query_lower in item.output_text.lower()
        ]

    def clear(self) -> None:
        """Limpia la memoria de trabajo."""
        self._buffer.clear()

    @property
    def size(self) -> int:
        """Número actual de elementos en la memoria."""
        return len(self._buffer)

    @property
    def capacity(self) -> int:
        """Capacidad máxima del buffer."""
        return self._capacity

    @property
    def is_empty(self) -> bool:
        return len(self._buffer) == 0

    def __repr__(self) -> str:
        return f"WorkingMemory({self.size}/{self.capacity} items)"
