"""Memoria episódica — experiencias completas almacenadas en SQLite.

Como los recuerdos autobiográficos humanos: cada experiencia se guarda
con su contexto temporal, emocional y resultado.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Episode:
    """Una experiencia almacenada."""

    id: Optional[int] = None
    timestamp: str = ""
    input_text: str = ""
    output_text: str = ""
    context: dict = field(default_factory=dict)
    emotion: str = "neutral"
    emotion_intensity: float = 0.5
    feedback_score: float = 0.0
    access_count: int = 0
    last_accessed: Optional[str] = None
    importance: float = 0.5


class EpisodicMemory:
    """Almacena experiencias completas en SQLite.

    Cada interacción se guarda como un episodio con metadatos ricos:
    emoción, feedback, importancia, contexto, timestamps.
    """

    def __init__(self, db_connection: sqlite3.Connection):
        self._conn = db_connection

    # ─── Almacenar ───────────────────────────────────────────

    def store(
        self,
        input_text: str,
        output_text: str = "",
        context: Optional[dict] = None,
        emotion: str = "neutral",
        emotion_intensity: float = 0.5,
        feedback_score: float = 0.0,
        importance: float = 0.5,
    ) -> int:
        """Guarda una nueva experiencia y devuelve su ID."""
        cursor = self._conn.execute(
            """
            INSERT INTO episodic_memory
                (input_text, output_text, context, emotion,
                 emotion_intensity, feedback_score, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                input_text,
                output_text,
                json.dumps(context or {}),
                emotion,
                emotion_intensity,
                feedback_score,
                importance,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    # ─── Recuperar ───────────────────────────────────────────

    def recall_recent(self, limit: int = 10) -> list[Episode]:
        """Devuelve las experiencias más recientes."""
        rows = self._conn.execute(
            """
            SELECT * FROM episodic_memory
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [self._row_to_episode(row) for row in rows]

    def recall_by_emotion(self, emotion: str, limit: int = 10) -> list[Episode]:
        """Recupera experiencias asociadas a una emoción."""
        rows = self._conn.execute(
            """
            SELECT * FROM episodic_memory
            WHERE emotion = ?
            ORDER BY emotion_intensity DESC, timestamp DESC
            LIMIT ?
            """,
            (emotion, limit),
        ).fetchall()
        return [self._row_to_episode(row) for row in rows]

    def recall_important(self, min_importance: float = 0.7, limit: int = 10) -> list[Episode]:
        """Recupera las experiencias más importantes."""
        rows = self._conn.execute(
            """
            SELECT * FROM episodic_memory
            WHERE importance >= ?
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
            """,
            (min_importance, limit),
        ).fetchall()
        return [self._row_to_episode(row) for row in rows]

    def recall_best_feedback(self, min_feedback: float = 0.5, limit: int = 5) -> list[Episode]:
        """Recupera experiencias con feedback positivo alto.

        Útil para dar ejemplos de "buenas respuestas" al módulo de razonamiento.
        """
        rows = self._conn.execute(
            """
            SELECT * FROM episodic_memory
            WHERE feedback_score >= ?
            ORDER BY feedback_score DESC, timestamp DESC
            LIMIT ?
            """,
            (min_feedback, limit),
        ).fetchall()
        return [self._row_to_episode(row) for row in rows]

    def search(self, query: str, limit: int = 10) -> list[Episode]:
        """Busca experiencias que contengan el texto dado."""
        pattern = f"%{query}%"
        rows = self._conn.execute(
            """
            SELECT * FROM episodic_memory
            WHERE input_text LIKE ? OR output_text LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (pattern, pattern, limit),
        ).fetchall()

        # Incrementar contador de acceso
        for row in rows:
            self._touch(row[0])

        return [self._row_to_episode(row) for row in rows]

    def get_by_id(self, episode_id: int) -> Optional[Episode]:
        """Recupera una experiencia por su ID."""
        row = self._conn.execute(
            "SELECT * FROM episodic_memory WHERE id = ?",
            (episode_id,),
        ).fetchone()
        if row:
            self._touch(episode_id)
            return self._row_to_episode(row)
        return None

    # ─── Feedback y actualización ────────────────────────────

    def update_feedback(self, episode_id: int, score: float) -> None:
        """Actualiza el feedback de una experiencia (-1.0 a 1.0)."""
        score = max(-1.0, min(1.0, score))
        self._conn.execute(
            """
            UPDATE episodic_memory
            SET feedback_score = ?, importance = MAX(importance, ABS(?))
            WHERE id = ?
            """,
            (score, score, episode_id),
        )
        self._conn.commit()

    def update_importance(self, episode_id: int, importance: float) -> None:
        """Ajusta la importancia de una experiencia."""
        importance = max(0.0, min(1.0, importance))
        self._conn.execute(
            "UPDATE episodic_memory SET importance = ? WHERE id = ?",
            (importance, episode_id),
        )
        self._conn.commit()

    # ─── Mantenimiento ───────────────────────────────────────

    def decay(self, days_threshold: int = 30, decay_factor: float = 0.9) -> int:
        """Reduce la importancia de recuerdos no accedidos recientemente.

        Returns:
            Número de recuerdos afectados.
        """
        cursor = self._conn.execute(
            """
            UPDATE episodic_memory
            SET importance = importance * ?
            WHERE last_accessed IS NOT NULL
              AND julianday('now') - julianday(last_accessed) > ?
              AND importance > 0.1
            """,
            (decay_factor, days_threshold),
        )
        self._conn.commit()
        return cursor.rowcount

    def count(self) -> int:
        """Número total de experiencias almacenadas."""
        row = self._conn.execute("SELECT COUNT(*) FROM episodic_memory").fetchone()
        return row[0] if row else 0

    def get_frequent_patterns(self, min_count: int = 3) -> list[dict]:
        """Identifica inputs que se repiten frecuentemente (para consolidación)."""
        rows = self._conn.execute(
            """
            SELECT input_text, COUNT(*) as freq, AVG(feedback_score) as avg_feedback
            FROM episodic_memory
            GROUP BY input_text
            HAVING freq >= ?
            ORDER BY freq DESC
            """,
            (min_count,),
        ).fetchall()
        return [
            {"input": row[0], "frequency": row[1], "avg_feedback": row[2]}
            for row in rows
        ]

    # ─── Privado ─────────────────────────────────────────────

    def _touch(self, episode_id: int) -> None:
        """Actualiza el timestamp y contador de acceso."""
        self._conn.execute(
            """
            UPDATE episodic_memory
            SET access_count = access_count + 1,
                last_accessed = datetime('now')
            WHERE id = ?
            """,
            (episode_id,),
        )
        self._conn.commit()

    @staticmethod
    def _row_to_episode(row: tuple) -> Episode:
        """Convierte una fila de SQLite en un Episode."""
        context = {}
        try:
            context = json.loads(row[4]) if row[4] else {}
        except (json.JSONDecodeError, TypeError):
            pass

        return Episode(
            id=row[0],
            timestamp=row[1],
            input_text=row[2],
            output_text=row[3],
            context=context,
            emotion=row[5],
            emotion_intensity=row[6],
            feedback_score=row[7],
            access_count=row[8],
            last_accessed=row[9],
            importance=row[10],
        )
