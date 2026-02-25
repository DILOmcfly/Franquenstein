"""Memoria emocional — asociaciones sentimentales a conceptos.

Como el instinto humano: recordamos cómo nos hicieron SENTIR las cosas
antes de recordar los detalles. Esto guía la toma de decisiones y
las respuestas del ser digital.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class EmotionalAssociation:
    """Una asociación emocional a un concepto."""

    id: Optional[int] = None
    concept: str = ""
    emotion: str = "neutral"
    intensity: float = 0.5
    occurrence_count: int = 1
    last_felt: str = ""


# Emociones disponibles para el ser digital
EMOTIONS = [
    "curiosidad",     # Quiere saber más
    "satisfaccion",   # La interacción fue positiva
    "confusion",      # No entiende algo
    "frustracion",    # Algo no funciona como esperaba
    "sorpresa",       # Algo inesperado
    "neutral",        # Sin emoción particular
    "alegria",        # Algo muy positivo
    "aburrimiento",   # Patrón repetitivo sin novedad
]


class EmotionalMemory:
    """Almacena asociaciones emocionales a conceptos y palabras.

    Cada concepto puede tener múltiples emociones asociadas con
    diferentes intensidades. Esto influye en cómo el ser responde
    a temas específicos.
    """

    def __init__(self, db_connection: sqlite3.Connection):
        self._conn = db_connection

    # ─── Registrar ───────────────────────────────────────────

    def feel(
        self,
        concept: str,
        emotion: str,
        intensity: float = 0.5,
    ) -> None:
        """Registra una emoción asociada a un concepto.

        Si la asociación ya existe, actualiza la intensidad
        promediándola con la nueva.
        """
        concept_lower = concept.lower().strip()
        emotion = emotion if emotion in EMOTIONS else "neutral"
        intensity = max(0.0, min(1.0, intensity))

        existing = self.get_emotion(concept_lower, emotion)
        if existing:
            # Promediar intensidad y contar ocurrencia
            new_intensity = (existing.intensity * 0.7) + (intensity * 0.3)
            self._conn.execute(
                """
                UPDATE emotional_memory
                SET intensity = ?,
                    occurrence_count = occurrence_count + 1,
                    last_felt = datetime('now')
                WHERE concept = ? AND emotion = ?
                """,
                (new_intensity, concept_lower, emotion),
            )
        else:
            self._conn.execute(
                """
                INSERT INTO emotional_memory (concept, emotion, intensity)
                VALUES (?, ?, ?)
                """,
                (concept_lower, emotion, intensity),
            )
        self._conn.commit()

    # ─── Consultar ───────────────────────────────────────────

    def get_emotion(self, concept: str, emotion: str) -> Optional[EmotionalAssociation]:
        """Busca una asociación emocional específica."""
        row = self._conn.execute(
            """
            SELECT * FROM emotional_memory
            WHERE concept = ? AND emotion = ?
            """,
            (concept.lower().strip(), emotion),
        ).fetchone()
        return self._row_to_association(row) if row else None

    def get_feelings_about(self, concept: str) -> list[EmotionalAssociation]:
        """Devuelve todas las emociones asociadas a un concepto."""
        rows = self._conn.execute(
            """
            SELECT * FROM emotional_memory
            WHERE concept = ?
            ORDER BY intensity DESC
            """,
            (concept.lower().strip(),),
        ).fetchall()
        return [self._row_to_association(row) for row in rows]

    def get_dominant_emotion(self, concept: str) -> Optional[EmotionalAssociation]:
        """Devuelve la emoción dominante para un concepto."""
        feelings = self.get_feelings_about(concept)
        return feelings[0] if feelings else None

    def get_mood(self) -> str:
        """Calcula el 'estado de ánimo' general basado en emociones recientes.

        Mira las emociones registradas en las últimas interacciones
        y devuelve la dominante.
        """
        row = self._conn.execute(
            """
            SELECT emotion, SUM(intensity * occurrence_count) as weight
            FROM emotional_memory
            ORDER BY last_felt DESC
            LIMIT 20
            """,
        ).fetchone()

        if row and row[0]:
            return row[0]
        return "curiosidad"  # Estado por defecto: curioso

    def search(self, query: str, limit: int = 10) -> list[EmotionalAssociation]:
        """Busca asociaciones emocionales por concepto."""
        pattern = f"%{query.lower()}%"
        rows = self._conn.execute(
            """
            SELECT * FROM emotional_memory
            WHERE concept LIKE ?
            ORDER BY intensity DESC
            LIMIT ?
            """,
            (pattern, limit),
        ).fetchall()
        return [self._row_to_association(row) for row in rows]

    # ─── Estadísticas ────────────────────────────────────────

    def count(self) -> int:
        """Número total de asociaciones emocionales."""
        row = self._conn.execute("SELECT COUNT(*) FROM emotional_memory").fetchone()
        return row[0] if row else 0

    def emotion_distribution(self) -> dict[str, int]:
        """Distribución de emociones registradas."""
        rows = self._conn.execute(
            """
            SELECT emotion, COUNT(*) FROM emotional_memory
            GROUP BY emotion
            ORDER BY COUNT(*) DESC
            """,
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    # ─── Privado ─────────────────────────────────────────────

    @staticmethod
    def _row_to_association(row: tuple) -> EmotionalAssociation:
        return EmotionalAssociation(
            id=row[0],
            concept=row[1],
            emotion=row[2],
            intensity=row[3],
            occurrence_count=row[4],
            last_felt=row[5],
        )
