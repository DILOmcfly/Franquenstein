"""Curiosity engine for proactive learning.

Selects low-confidence concepts and generates exploratory Q&A cycles.
"""

from __future__ import annotations

from typing import Any


class CuriosityEngine:
    """Run small autonomous curiosity cycles."""

    def __init__(self, memory, reasoner):
        self.memory = memory
        self.reasoner = reasoner

    @staticmethod
    def _curiosity_score(concept) -> float:
        """Rank concepts by pedagogical value (v2 heuristic)."""
        uncertainty = 1.0 - float(concept.confidence)
        connectivity = len(concept.associations or []) * 0.2
        reinforcement_bonus = min(0.4, float(concept.source_count) * 0.03)
        return uncertainty + connectivity + reinforcement_bonus

    def explore_once(self, level_name: str = "Niño", mood: str = "curiosidad") -> dict[str, Any]:
        """Execute one curiosity step.

        Returns a dict describing what happened.
        """
        candidates = self.memory.semantic.get_least_confident(limit=8)
        if not candidates:
            return {"status": "no_candidates", "question": "", "answer": ""}

        concept = max(candidates, key=self._curiosity_score)
        question = f"¿Qué debería entender mejor sobre '{concept.concept}' y por qué importa?"

        answer = ""
        if self.reasoner and self.reasoner.is_available():
            try:
                answer = self.reasoner.generate(
                    input_text=question,
                    level_name=level_name,
                    mood=mood,
                    working_memory=[],
                    known_concepts=[c.concept for c in candidates],
                    good_examples=None,
                    user_name="",
                )
            except Exception:
                answer = ""

        if not answer:
            answer = (
                f"'{concept.concept}' parece importante porque se conecta con otras ideas. "
                "Necesito más ejemplos para entenderlo mejor."
            )

        self.memory.remember(
            input_text=question,
            output_text=answer,
            emotion="curiosidad",
            emotion_intensity=0.8,
            feedback_score=0.3,
            importance=0.6,
        )

        self.memory.semantic.learn_concept(
            concept=concept.concept,
            definition=answer[:200],
            initial_confidence=min(0.6, concept.confidence + 0.1),
        )

        return {
            "status": "ok",
            "concept": concept.concept,
            "question": question,
            "answer": answer,
            "score": round(self._curiosity_score(concept), 3),
        }
