"""Metacognition — the being's ability to reflect on its own performance.

This is the "thinking about thinking" module. Periodically, the being
reviews its past responses, evaluates what worked and what didn't,
and generates insights that improve future reasoning.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from franquenstein.memory.episodic import EpisodicMemory, Episode
from franquenstein.memory.memory import MemorySystem


@dataclass
class Reflection:
    """A self-reflection by the being."""

    timestamp: str
    insight: str
    category: str  # "strength", "weakness", "observation", "goal"
    confidence: float
    source_episodes: list[int]


class MetaCognition:
    """Self-evaluation and reflection system.

    The being periodically reviews its interactions and generates
    insights about its own performance. These reflections feed
    back into the reasoning process.
    """

    def __init__(self, memory: MemorySystem):
        self._memory = memory
        self._reflections: list[Reflection] = []
        self._load_reflections()

    # ─── Self-Evaluation ─────────────────────────────────────

    def evaluate_interaction(
        self,
        episode_id: int,
        feedback_score: float,
    ) -> Optional[Reflection]:
        """Evaluate a single interaction and potentially generate a reflection.

        Called after receiving feedback on a response.
        """
        episode = self._memory.episodic.get_by_id(episode_id)
        if not episode:
            return None

        # Update the episode's feedback
        self._memory.episodic.update_feedback(episode_id, feedback_score)

        # Generate reflection if feedback is strongly positive or negative
        if abs(feedback_score) >= 0.5:
            return self._generate_reflection(episode, feedback_score)

        return None

    def reflect(self, n_recent: int = 20) -> list[Reflection]:
        """Perform a reflection session over recent interactions.

        Reviews the last N interactions and generates insights.
        This is like "sleeping" — processing the day's experiences.
        """
        episodes = self._memory.episodic.recall_recent(limit=n_recent)
        if not episodes:
            return []

        new_reflections: list[Reflection] = []

        # Analyze feedback distribution
        positive = [e for e in episodes if e.feedback_score > 0.3]
        negative = [e for e in episodes if e.feedback_score < -0.3]
        neutral = [e for e in episodes if -0.3 <= e.feedback_score <= 0.3]

        # Insight: What types of responses work well?
        if len(positive) > len(negative) * 2:
            r = Reflection(
                timestamp=datetime.now().isoformat(),
                insight="Most recent interactions were positive. Current approach is working well.",
                category="strength",
                confidence=0.7,
                source_episodes=[e.id for e in positive if e.id],
            )
            new_reflections.append(r)
        elif len(negative) > len(positive):
            r = Reflection(
                timestamp=datetime.now().isoformat(),
                insight="More negative than positive interactions recently. Need to adjust approach.",
                category="weakness",
                confidence=0.7,
                source_episodes=[e.id for e in negative if e.id],
            )
            new_reflections.append(r)

        # Insight: Emotional patterns
        emotion_counts: dict[str, int] = {}
        for e in episodes:
            emotion_counts[e.emotion] = emotion_counts.get(e.emotion, 0) + 1

        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"
        if dominant_emotion != "neutral":
            r = Reflection(
                timestamp=datetime.now().isoformat(),
                insight=f"Dominant emotional state recently: {dominant_emotion}",
                category="observation",
                confidence=0.6,
                source_episodes=[],
            )
            new_reflections.append(r)

        # Insight: Learning rate
        total_experiences = self._memory.episodic.count()
        vocab = self._memory.semantic.vocabulary_size()
        if total_experiences > 0:
            learning_efficiency = vocab / max(1, total_experiences)
            if learning_efficiency > 0.3:
                r = Reflection(
                    timestamp=datetime.now().isoformat(),
                    insight=f"Learning efficiently: {vocab} concepts from {total_experiences} experiences.",
                    category="strength",
                    confidence=0.5,
                    source_episodes=[],
                )
                new_reflections.append(r)

        # Store reflections
        for ref in new_reflections:
            self._reflections.append(ref)
        self._save_reflections()

        return new_reflections

    def get_recent_reflections(self, n: int = 5) -> list[Reflection]:
        """Get the most recent reflections."""
        return self._reflections[-n:]

    def get_strengths(self) -> list[Reflection]:
        """Get identified strengths."""
        return [r for r in self._reflections if r.category == "strength"]

    def get_weaknesses(self) -> list[Reflection]:
        """Get identified weaknesses."""
        return [r for r in self._reflections if r.category == "weakness"]

    # ─── Internal ────────────────────────────────────────────

    def _generate_reflection(
        self,
        episode: Episode,
        feedback_score: float,
    ) -> Reflection:
        """Generate a reflection from a single episode."""
        if feedback_score > 0:
            insight = (
                f"Good response to '{episode.input_text[:50]}' "
                f"(score: {feedback_score:.1f}). "
                "This type of response works."
            )
            category = "strength"
        else:
            insight = (
                f"Poor response to '{episode.input_text[:50]}' "
                f"(score: {feedback_score:.1f}). "
                "Should find a better approach for this."
            )
            category = "weakness"

        r = Reflection(
            timestamp=datetime.now().isoformat(),
            insight=insight,
            category=category,
            confidence=min(1.0, abs(feedback_score)),
            source_episodes=[episode.id] if episode.id else [],
        )
        self._reflections.append(r)
        self._save_reflections()
        return r

    def _save_reflections(self) -> None:
        """Persist reflections to the being's state."""
        # Keep only last 50 reflections to avoid unbounded growth
        trimmed = self._reflections[-50:]
        data = json.dumps([
            {
                "timestamp": r.timestamp,
                "insight": r.insight,
                "category": r.category,
                "confidence": r.confidence,
                "source_episodes": r.source_episodes,
            }
            for r in trimmed
        ])
        self._memory.save_state("reflections", data)

    def _load_reflections(self) -> None:
        """Load saved reflections from persistent state."""
        data = self._memory.load_state("reflections", "[]")
        try:
            items = json.loads(data)
            self._reflections = [
                Reflection(
                    timestamp=item["timestamp"],
                    insight=item["insight"],
                    category=item["category"],
                    confidence=item["confidence"],
                    source_episodes=item.get("source_episodes", []),
                )
                for item in items
            ]
        except (json.JSONDecodeError, KeyError):
            self._reflections = []
