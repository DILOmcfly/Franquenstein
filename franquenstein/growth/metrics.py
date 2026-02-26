"""Performance metrics — tracks the being's development over time.

Measures vocabulary growth, interaction quality, learning speed,
emotional balance, and other indicators of cognitive development.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from franquenstein.memory.memory import MemorySystem


@dataclass
class MetricsSnapshot:
    """A snapshot of the being's performance at a point in time."""

    timestamp: str
    total_experiences: int
    vocabulary_size: int
    emotional_associations: int
    avg_feedback: float
    dominant_emotion: str
    learning_efficiency: float  # concepts per experience
    memory_utilization: float   # working memory usage ratio


class Metrics:
    """Tracks development metrics for the being.

    These metrics drive the growth/leveling system and provide
    insight into the being's cognitive development.
    """

    def __init__(self, memory: MemorySystem):
        self._memory = memory

    def snapshot(self) -> MetricsSnapshot:
        """Take a snapshot of current performance metrics."""
        stats = self._memory.get_stats()
        total_exp = stats["episodic_memories"]
        vocab = stats["semantic_concepts"]

        # Calculate averages from recent episodes
        recent = self._memory.episodic.recall_recent(limit=50)
        avg_feedback = 0.0
        if recent:
            scores = [e.feedback_score for e in recent]
            avg_feedback = sum(scores) / len(scores)

        # Learning efficiency: how many concepts per experience
        efficiency = vocab / max(1, total_exp)

        # Working memory utilization
        wm_parts = stats["working_memory"].split("/")
        wm_used = int(wm_parts[0]) if len(wm_parts) == 2 else 0
        wm_total = int(wm_parts[1]) if len(wm_parts) == 2 else 1
        utilization = wm_used / max(1, wm_total)

        return MetricsSnapshot(
            timestamp=datetime.now().isoformat(),
            total_experiences=total_exp,
            vocabulary_size=vocab,
            emotional_associations=stats["emotional_associations"],
            avg_feedback=round(avg_feedback, 3),
            dominant_emotion=stats["mood"],
            learning_efficiency=round(efficiency, 3),
            memory_utilization=round(utilization, 2),
        )

    def get_development_summary(self) -> dict:
        """Get a human-readable development summary."""
        snap = self.snapshot()
        return {
            "experiences": snap.total_experiences,
            "vocabulary": snap.vocabulary_size,
            "emotions": snap.emotional_associations,
            "feedback_avg": snap.avg_feedback,
            "mood": snap.dominant_emotion,
            "efficiency": f"{snap.learning_efficiency:.1%}",
        }
