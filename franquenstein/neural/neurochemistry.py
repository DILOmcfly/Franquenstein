"""Virtual neurochemistry for neuromodulated cognition."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Neurochemistry:
    dopamine: float = 0.5
    serotonin: float = 0.5
    norepinephrine: float = 0.3
    cortisol: float = 0.1
    oxytocin: float = 0.3

    def _clamp(self) -> None:
        for k, v in asdict(self).items():
            setattr(self, k, max(0.0, min(1.0, float(v))))

    def modulate(self, event: str) -> None:
        e = event.lower().strip()
        if e == "feedback_positive":
            self.dopamine += 0.15
            self.oxytocin += 0.10
            self.cortisol -= 0.05
        elif e == "feedback_negative":
            self.dopamine -= 0.10
            self.cortisol += 0.15
            self.norepinephrine += 0.10
        elif e == "curiosity_discovery":
            self.dopamine += 0.20
            self.serotonin += 0.10
        elif e == "unanswered":
            self.cortisol += 0.10
            self.norepinephrine += 0.15
        elif e == "social_trust":
            self.oxytocin += 0.08
            self.serotonin += 0.04
        elif e == "novel_input":
            self.norepinephrine += 0.08
            self.dopamine += 0.04

        self._clamp()

    def homeostasis(self, speed: float = 0.02) -> None:
        baseline = {
            "dopamine": 0.5,
            "serotonin": 0.5,
            "norepinephrine": 0.3,
            "cortisol": 0.1,
            "oxytocin": 0.3,
        }
        for k, b in baseline.items():
            cur = getattr(self, k)
            setattr(self, k, cur + (b - cur) * speed)
        self._clamp()

    def get_graph_params(self) -> dict:
        # Higher serotonin broadens thought; cortisol narrows it.
        max_depth = int(round(4 + self.serotonin * 2 - self.cortisol * 2))
        max_depth = max(2, min(7, max_depth))

        # More norepinephrine lowers threshold (more sensitive),
        # cortisol raises threshold (defensive processing).
        threshold = 0.15 * (1.0 - self.norepinephrine * 0.25 + self.cortisol * 0.35)
        threshold = max(0.06, min(0.4, threshold))

        decay_factor = 0.6 * (1.0 + self.serotonin * 0.2 - self.cortisol * 0.25)
        decay_factor = max(0.35, min(0.9, decay_factor))

        plasticity = 1.0 + self.dopamine * 0.5 - self.cortisol * 0.3
        plasticity = max(0.6, min(1.8, plasticity))

        return {
            "activation_threshold": threshold,
            "decay_factor": decay_factor,
            "max_propagation_depth": max_depth,
            "plasticity": plasticity,
        }

    def get_tone(self) -> str:
        if self.cortisol > 0.6:
            return "defensive"
        if self.dopamine > 0.65 and self.oxytocin > 0.45:
            return "warm"
        if self.norepinephrine > 0.6:
            return "focused"
        if self.serotonin > 0.65:
            return "reflective"
        return "neutral"

    def to_state(self) -> dict:
        return asdict(self)

    @classmethod
    def from_state(cls, state: dict | None) -> "Neurochemistry":
        if not state:
            return cls()
        return cls(**{k: float(v) for k, v in state.items() if k in cls.__annotations__})
