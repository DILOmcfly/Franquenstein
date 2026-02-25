"""Unified Memory System — orchestrates all 4 memory layers.

This is the main entry point for all memory operations.
It manages the SQLite database, coordinates between layers,
and handles consolidation (episodic → semantic).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

import franquenstein.config as cfg
from franquenstein.memory.working import WorkingMemory, WorkingMemoryItem
from franquenstein.memory.episodic import EpisodicMemory, Episode
from franquenstein.memory.semantic import SemanticMemory, Concept
from franquenstein.memory.emotional import EmotionalMemory, EmotionalAssociation


class MemorySystem:
    """Orchestrates the 4-layer memory system.

    Layers:
        - Working: RAM-only, last N interactions (immediate context)
        - Episodic: SQLite, full experiences with emotions and feedback
        - Semantic: SQLite, consolidated facts and concepts
        - Emotional: SQLite, sentiment associations to concepts
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or cfg.DB_PATH
        self._conn = self._init_database()

        # Initialize all memory layers
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory(self._conn)
        self.semantic = SemanticMemory(self._conn)
        self.emotional = EmotionalMemory(self._conn)

    # ─── Database ────────────────────────────────────────────

    def _init_database(self) -> sqlite3.Connection:
        """Initialize SQLite database with schema."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA cache_size=-8000")  # ~8MB page cache
        conn.execute("PRAGMA foreign_keys=ON")

        # Load and execute schema
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        return conn

    # ─── High-level API ──────────────────────────────────────

    def remember(
        self,
        input_text: str,
        output_text: str = "",
        emotion: str = "neutral",
        emotion_intensity: float = 0.5,
        feedback_score: float = 0.0,
        importance: float = 0.5,
    ) -> int:
        """Store a complete interaction across all relevant memory layers.

        This is the main method for recording new experiences.
        It stores in working memory, episodic memory, and
        registers emotional associations.

        Returns:
            The episode ID from episodic memory.
        """
        # 1. Working memory — immediate context
        self.working.push(WorkingMemoryItem(
            input_text=input_text,
            output_text=output_text,
            emotion=emotion,
        ))

        # 2. Episodic memory — persistent experience
        episode_id = self.episodic.store(
            input_text=input_text,
            output_text=output_text,
            emotion=emotion,
            emotion_intensity=emotion_intensity,
            feedback_score=feedback_score,
            importance=importance,
        )

        # 3. Emotional memory — associate emotions with key words
        words = self._extract_key_words(input_text)
        for word in words:
            self.emotional.feel(word, emotion, emotion_intensity)

        return episode_id

    def recall(self, query: str, limit: int = 5) -> dict:
        """Search across all memory layers for relevant memories.

        Returns a dict with results from each layer.
        """
        return {
            "working": self.working.search(query),
            "episodic": self.episodic.search(query, limit=limit),
            "semantic": self.semantic.search(query, limit=limit),
            "emotional": self.emotional.search(query, limit=limit),
        }

    def get_context(self) -> dict:
        """Get the current cognitive context for reasoning.

        Returns all relevant information the being needs to
        formulate a response.
        """
        return {
            "recent_context": self.working.get_context_string(),
            "mood": self.emotional.get_mood(),
            "working_memory_size": self.working.size,
            "total_experiences": self.episodic.count(),
            "vocabulary_size": self.semantic.vocabulary_size(),
            "emotional_associations": self.emotional.count(),
        }

    # ─── Consolidation ───────────────────────────────────────

    def consolidate(self) -> int:
        """Move repeated patterns from episodic to semantic memory.

        This is like "sleeping" — the being processes its experiences
        and extracts general knowledge from repeated patterns.

        Returns:
            Number of new concepts consolidated.
        """
        patterns = self.episodic.get_frequent_patterns(
            min_count=cfg.CONSOLIDATION_THRESHOLD
        )
        consolidated = 0

        for pattern in patterns:
            concept_id = self.semantic.consolidate_from_episodes(
                input_text=pattern["input"],
                frequency=pattern["frequency"],
                avg_feedback=pattern["avg_feedback"],
            )
            if concept_id is not None:
                consolidated += 1

        return consolidated

    def maintenance(self) -> dict:
        """Perform memory maintenance: decay old memories, consolidate patterns.

        Should be called periodically (e.g., at startup or every N interactions).
        """
        decayed = self.episodic.decay(days_threshold=cfg.MEMORY_DECAY_DAYS)
        consolidated = self.consolidate()

        return {
            "memories_decayed": decayed,
            "concepts_consolidated": consolidated,
        }

    # ─── State Persistence ───────────────────────────────────

    def save_state(self, key: str, value: str) -> None:
        """Save a key-value pair to persistent being state."""
        self._conn.execute(
            """
            INSERT INTO being_state (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = datetime('now')
            """,
            (key, value, value),
        )
        self._conn.commit()

    def load_state(self, key: str, default: str = "") -> str:
        """Load a value from persistent being state."""
        row = self._conn.execute(
            "SELECT value FROM being_state WHERE key = ?",
            (key,),
        ).fetchone()
        return row[0] if row else default

    # ─── Statistics ──────────────────────────────────────────

    def get_stats(self) -> dict:
        """Get memory system statistics."""
        return {
            "working_memory": f"{self.working.size}/{self.working.capacity}",
            "episodic_memories": self.episodic.count(),
            "semantic_concepts": self.semantic.count(),
            "emotional_associations": self.emotional.count(),
            "mood": self.emotional.get_mood(),
        }

    # ─── Helpers ─────────────────────────────────────────────

    @staticmethod
    def _extract_key_words(text: str) -> list[str]:
        """Extract meaningful words from text (simple approach).

        Filters out very short words and common stop words.
        This can evolve as the being learns.
        """
        stop_words = {
            "el", "la", "los", "las", "un", "una", "de", "del", "en",
            "y", "o", "a", "que", "es", "se", "no", "por", "con",
            "the", "a", "an", "is", "are", "was", "were", "in", "on",
            "at", "to", "for", "of", "and", "or", "but", "not", "with",
            "i", "you", "he", "she", "it", "we", "they", "my", "your",
            "yo", "tu", "su", "mi", "me", "te", "nos",
        }
        words = text.lower().split()
        return [
            w.strip(".,!?¿¡;:\"'()[]{}") for w in words
            if len(w) > 2 and w.lower().strip(".,!?¿¡;:\"'()[]{}") not in stop_words
        ]

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
