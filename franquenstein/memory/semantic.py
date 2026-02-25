"""Memoria semántica — hechos y conceptos aprendidos.

Como el conocimiento general humano: no recuerdas CUÁNDO aprendiste
que "el fuego quema", simplemente lo sabes. Los hechos se consolidan
desde la memoria episódica cuando se repiten lo suficiente.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Concept:
    """Un concepto almacenado en la memoria semántica."""

    id: Optional[int] = None
    concept: str = ""
    definition: str = ""
    associations: list[str] = field(default_factory=list)
    confidence: float = 0.1
    source_count: int = 1
    first_learned: str = ""
    last_reinforced: str = ""


class SemanticMemory:
    """Almacena hechos y conceptos aprendidos.

    Los conceptos se crean cuando un patrón se repite lo suficiente
    en la memoria episódica (consolidación). Su confianza crece con
    cada refuerzo.
    """

    def __init__(self, db_connection: sqlite3.Connection):
        self._conn = db_connection

    # ─── Almacenar / Reforzar ────────────────────────────────

    def learn_concept(
        self,
        concept: str,
        definition: str = "",
        associations: Optional[list[str]] = None,
        initial_confidence: float = 0.1,
    ) -> int:
        """Aprende un concepto nuevo o refuerza uno existente.

        Si el concepto ya existe, incrementa su confianza y source_count.
        """
        concept_lower = concept.lower().strip()
        existing = self.get_concept(concept_lower)

        if existing:
            # Reforzar concepto existente
            new_confidence = min(1.0, existing.confidence + 0.1)
            new_associations = list(
                set(existing.associations + (associations or []))
            )
            self._conn.execute(
                """
                UPDATE semantic_memory
                SET confidence = ?,
                    source_count = source_count + 1,
                    associations = ?,
                    last_reinforced = datetime('now')
                WHERE concept = ?
                """,
                (new_confidence, json.dumps(new_associations), concept_lower),
            )
            self._conn.commit()
            return existing.id  # type: ignore[return-value]
        else:
            # Aprender concepto nuevo
            cursor = self._conn.execute(
                """
                INSERT INTO semantic_memory (concept, definition, associations, confidence)
                VALUES (?, ?, ?, ?)
                """,
                (
                    concept_lower,
                    definition,
                    json.dumps(associations or []),
                    initial_confidence,
                ),
            )
            self._conn.commit()
            return cursor.lastrowid  # type: ignore[return-value]

    def add_association(self, concept: str, associated_concept: str) -> bool:
        """Añade una asociación entre dos conceptos."""
        concept_lower = concept.lower().strip()
        existing = self.get_concept(concept_lower)
        if not existing:
            return False

        associations = list(set(existing.associations + [associated_concept.lower().strip()]))
        self._conn.execute(
            "UPDATE semantic_memory SET associations = ? WHERE concept = ?",
            (json.dumps(associations), concept_lower),
        )
        self._conn.commit()
        return True

    # ─── Recuperar ───────────────────────────────────────────

    def get_concept(self, concept: str) -> Optional[Concept]:
        """Busca un concepto por nombre exacto."""
        row = self._conn.execute(
            "SELECT * FROM semantic_memory WHERE concept = ?",
            (concept.lower().strip(),),
        ).fetchone()
        return self._row_to_concept(row) if row else None

    def search(self, query: str, limit: int = 10) -> list[Concept]:
        """Busca conceptos que contengan el texto dado."""
        pattern = f"%{query.lower()}%"
        rows = self._conn.execute(
            """
            SELECT * FROM semantic_memory
            WHERE concept LIKE ? OR definition LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
            """,
            (pattern, pattern, limit),
        ).fetchall()
        return [self._row_to_concept(row) for row in rows]

    def get_related(self, concept: str, limit: int = 5) -> list[Concept]:
        """Encuentra conceptos relacionados (por asociaciones)."""
        main = self.get_concept(concept)
        if not main or not main.associations:
            return []

        related: list[Concept] = []
        for assoc in main.associations[:limit]:
            c = self.get_concept(assoc)
            if c:
                related.append(c)
        return related

    def get_confident(self, min_confidence: float = 0.5, limit: int = 20) -> list[Concept]:
        """Devuelve conceptos con alta confianza (bien aprendidos)."""
        rows = self._conn.execute(
            """
            SELECT * FROM semantic_memory
            WHERE confidence >= ?
            ORDER BY confidence DESC
            LIMIT ?
            """,
            (min_confidence, limit),
        ).fetchall()
        return [self._row_to_concept(row) for row in rows]

    def get_least_confident(self, limit: int = 10) -> list[Concept]:
        """Devuelve conceptos menos confiados (candidatos para curiosidad)."""
        rows = self._conn.execute(
            """
            SELECT * FROM semantic_memory
            ORDER BY confidence ASC, last_reinforced ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [self._row_to_concept(row) for row in rows]

    # ─── Consolidación ───────────────────────────────────────

    def consolidate_from_episodes(
        self,
        input_text: str,
        frequency: int,
        avg_feedback: float,
    ) -> Optional[int]:
        """Consolida un patrón episódico repetido en un concepto semántico.

        Se llama cuando la memoria episódica detecta que un input
        se ha repetido lo suficiente.
        """
        # Extraer palabras clave del input como concepto
        words = input_text.lower().strip().split()
        if not words:
            return None

        # El concepto es la frase o la palabra más relevante
        concept_key = input_text.lower().strip() if len(words) <= 3 else " ".join(words[:3])

        confidence = min(1.0, 0.1 + (frequency * 0.1) + max(0, avg_feedback * 0.2))
        return self.learn_concept(
            concept=concept_key,
            definition=f"Patrón consolidado de {frequency} experiencias",
            initial_confidence=confidence,
        )

    # ─── Estadísticas ────────────────────────────────────────

    def count(self) -> int:
        """Número total de conceptos aprendidos."""
        row = self._conn.execute("SELECT COUNT(*) FROM semantic_memory").fetchone()
        return row[0] if row else 0

    def vocabulary_size(self) -> int:
        """Alias de count — útil para el sistema de crecimiento."""
        return self.count()

    # ─── Privado ─────────────────────────────────────────────

    @staticmethod
    def _row_to_concept(row: tuple) -> Concept:
        associations: list[str] = []
        try:
            associations = json.loads(row[3]) if row[3] else []
        except (json.JSONDecodeError, TypeError):
            pass

        return Concept(
            id=row[0],
            concept=row[1],
            definition=row[2] or "",
            associations=associations,
            confidence=row[4],
            source_count=row[5],
            first_learned=row[6],
            last_reinforced=row[7],
        )
