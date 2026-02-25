"""Learner — main learning orchestrator for the being.

Coordinates pattern detection, feedback processing, and metacognition
into a unified learning loop. Every interaction feeds through here.
"""

from __future__ import annotations

from typing import Optional

from franquenstein.memory.memory import MemorySystem
from franquenstein.learning.patterns import PatternDetector
from franquenstein.learning.metacognition import MetaCognition, Reflection
from franquenstein.config import (
    FEEDBACK_POSITIVE_BOOST,
    FEEDBACK_NEGATIVE_PENALTY,
)


class Learner:
    """The being's learning engine.

    Three learning strategies:
    1. Learning by repetition — patterns that repeat become knowledge
    2. Learning by feedback — user tells us what was good/bad
    3. Learning by reflection — periodic self-evaluation

    The learner ties together pattern detection, semantic memory
    consolidation, and metacognitive reflection.
    """

    def __init__(self, memory: MemorySystem):
        self._memory = memory
        self._patterns = PatternDetector(memory._conn)
        self._metacognition = MetaCognition(memory)
        self._interaction_count = 0
        self._session_feedback: list[float] = []

    # ─── Core Learning Loop ──────────────────────────────────

    def learn_from_interaction(
        self,
        input_text: str,
        output_text: str,
        emotion: str = "neutral",
        emotion_intensity: float = 0.5,
    ) -> dict:
        """Process a complete interaction and extract learning.

        This is the main entry point — called after every interaction.

        Returns a dict with learning outcomes.
        """
        self._interaction_count += 1

        # 1. Observe patterns in the input
        new_patterns = self._patterns.observe(input_text)

        # 2. Store in memory
        episode_id = self._memory.remember(
            input_text=input_text,
            output_text=output_text,
            emotion=emotion,
            emotion_intensity=emotion_intensity,
        )

        # 3. Learn words as semantic concepts
        words = self._memory._extract_key_words(input_text)
        for word in words:
            self._memory.semantic.learn_concept(
                concept=word,
                definition="",  # Will be enriched over time
            )

        # 4. Periodically consolidate and reflect
        consolidation_result = None
        reflections = None
        if self._interaction_count % 10 == 0:
            consolidation_result = self._memory.consolidate()
        if self._interaction_count % 20 == 0:
            reflections = self._metacognition.reflect()

        return {
            "episode_id": episode_id,
            "new_patterns": len(new_patterns),
            "words_observed": len(words),
            "consolidated": consolidation_result,
            "reflections": len(reflections) if reflections else 0,
        }

    def process_feedback(
        self,
        episode_id: int,
        score: float,
        input_text: str = "",
        output_text: str = "",
    ) -> Optional[Reflection]:
        """Process user feedback on a response.

        Score: -1.0 (terrible) to 1.0 (excellent)

        Returns a reflection if the feedback triggered self-evaluation.
        """
        score = max(-1.0, min(1.0, score))
        self._session_feedback.append(score)

        # Update episodic memory
        self._memory.episodic.update_feedback(episode_id, score)

        # Update response pattern
        if input_text and output_text:
            self._patterns.observe_response(input_text, output_text, score)

        # Adjust emotional memory
        words = self._memory._extract_key_words(input_text) if input_text else []
        emotion = "satisfaccion" if score > 0 else "frustracion"
        for word in words:
            self._memory.emotional.feel(word, emotion, abs(score))

        # Metacognitive evaluation
        return self._metacognition.evaluate_interaction(episode_id, score)

    # ─── Reasoning Support ───────────────────────────────────

    def suggest_response(self, input_text: str) -> Optional[str]:
        """Check if we have a learned response pattern for this input.

        Returns the best known response if one exists with sufficient
        confidence, otherwise None (and the being must reason on its own).
        """
        return self._patterns.get_best_response(input_text)

    def get_relevant_knowledge(self, input_text: str) -> dict:
        """Gather all relevant knowledge for formulating a response.

        Searches across memory layers and patterns for anything
        related to the input.
        """
        # Search memory
        memories = self._memory.recall(input_text)

        # Get known words in the input
        words = self._memory._extract_key_words(input_text)
        known_concepts = []
        for word in words:
            concept = self._memory.semantic.get_concept(word)
            if concept and concept.confidence > 0.2:
                known_concepts.append(concept)

        # Get emotional associations
        emotions_about = {}
        for word in words:
            dominant = self._memory.emotional.get_dominant_emotion(word)
            if dominant:
                emotions_about[word] = dominant.emotion

        # Get recent reflections
        reflections = self._metacognition.get_recent_reflections(3)

        return {
            "working_context": memories["working"],
            "related_episodes": memories["episodic"][:3],
            "known_concepts": known_concepts,
            "emotions_about": emotions_about,
            "recent_reflections": [r.insight for r in reflections],
        }

    # ─── Statistics ──────────────────────────────────────────

    def get_stats(self) -> dict:
        """Get learning engine statistics."""
        avg_feedback = (
            sum(self._session_feedback) / len(self._session_feedback)
            if self._session_feedback
            else 0.0
        )
        return {
            "interactions_this_session": self._interaction_count,
            "known_words": self._patterns.get_word_count(),
            "session_avg_feedback": round(avg_feedback, 2),
            "total_reflections": len(self._metacognition.get_recent_reflections(100)),
            "strengths": len(self._metacognition.get_strengths()),
            "weaknesses": len(self._metacognition.get_weaknesses()),
        }

    @property
    def patterns(self) -> PatternDetector:
        return self._patterns

    @property
    def metacognition(self) -> MetaCognition:
        return self._metacognition
