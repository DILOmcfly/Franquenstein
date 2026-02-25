"""Growth System — capability levels and milestones.

The being starts as Level 0 (Baby) and grows by accumulating
experiences and vocabulary. Each level unlocks new capabilities
that change how the being responds and reasons.
"""

from __future__ import annotations

import json
from typing import Optional

from franquenstein.config import GROWTH_LEVELS
from franquenstein.memory.memory import MemorySystem
from franquenstein.growth.metrics import Metrics, MetricsSnapshot


class GrowthSystem:
    """Manages the being's growth from baby to sage.

    Levels are earned by accumulating experiences and vocabulary.
    Each level unlocks new behavioral capabilities.
    """

    def __init__(self, memory: MemorySystem):
        self._memory = memory
        self._metrics = Metrics(memory)
        self._level = self._load_level()
        self._capabilities = self._get_capabilities_for_level(self._level)

    # ─── Growth Check ────────────────────────────────────────

    def check_growth(self) -> Optional[dict]:
        """Check if the being should level up.

        Returns level-up info if a new level was reached, else None.
        """
        snap = self._metrics.snapshot()
        new_level = self._calculate_level(snap)

        if new_level > self._level:
            old_level = self._level
            self._level = new_level
            self._capabilities = self._get_capabilities_for_level(new_level)
            self._save_level()

            return {
                "old_level": old_level,
                "new_level": new_level,
                "old_name": GROWTH_LEVELS.get(old_level, {}).get("name", "?"),
                "new_name": GROWTH_LEVELS.get(new_level, {}).get("name", "?"),
                "new_capabilities": self._capabilities,
            }

        return None

    def _calculate_level(self, snap: MetricsSnapshot) -> int:
        """Determine the appropriate level based on metrics."""
        current_level = 0
        for level, requirements in sorted(GROWTH_LEVELS.items()):
            if (
                snap.vocabulary_size >= requirements["vocab_needed"]
                and snap.total_experiences >= requirements["experiences_needed"]
            ):
                current_level = level
            else:
                break
        return current_level

    # ─── Capabilities ────────────────────────────────────────

    def _get_capabilities_for_level(self, level: int) -> list[str]:
        """Return the capabilities unlocked at a given level."""
        capabilities_map = {
            0: [
                "echo",           # Can repeat what it hears
                "basic_response", # Can give simple responses
            ],
            1: [
                "remember_name",     # Can remember the user's name
                "recognize_keywords",# Can respond to known words
                "show_emotion",      # Can express basic emotions
            ],
            2: [
                "form_associations", # Can connect related concepts
                "ask_questions",     # Can ask the user questions
                "recall_memories",   # Can reference past interactions
            ],
            3: [
                "basic_reasoning",      # Can make simple logical connections
                "detect_contradictions", # Can notice inconsistencies
                "express_preferences",   # Can state likes/dislikes
            ],
            4: [
                "complex_reasoning",     # Can chain multiple ideas
                "self_optimization",     # Can suggest improvements to itself
                "teach_back",            # Can explain what it has learned
            ],
            5: [
                "emergent",  # New capabilities based on learned patterns
            ],
        }

        # Accumulate capabilities from all levels up to current
        all_caps: list[str] = []
        for lvl in range(level + 1):
            all_caps.extend(capabilities_map.get(lvl, []))
        return all_caps

    def can(self, capability: str) -> bool:
        """Check if the being has a specific capability."""
        return capability in self._capabilities

    # ─── State ───────────────────────────────────────────────

    @property
    def level(self) -> int:
        return self._level

    @property
    def level_name(self) -> str:
        return GROWTH_LEVELS.get(self._level, {}).get("name", "Unknown")

    @property
    def capabilities(self) -> list[str]:
        return list(self._capabilities)

    def get_progress(self) -> dict:
        """Get progress towards the next level."""
        snap = self._metrics.snapshot()
        next_level = self._level + 1

        if next_level not in GROWTH_LEVELS:
            return {
                "current_level": self._level,
                "current_name": self.level_name,
                "next_level": None,
                "message": "Maximum level reached!",
            }

        next_req = GROWTH_LEVELS[next_level]
        vocab_progress = snap.vocabulary_size / max(1, next_req["vocab_needed"])
        exp_progress = snap.total_experiences / max(1, next_req["experiences_needed"])

        return {
            "current_level": self._level,
            "current_name": self.level_name,
            "next_level": next_level,
            "next_name": next_req["name"],
            "vocabulary": f"{snap.vocabulary_size}/{next_req['vocab_needed']}",
            "experiences": f"{snap.total_experiences}/{next_req['experiences_needed']}",
            "vocab_progress": f"{min(100, vocab_progress * 100):.0f}%",
            "exp_progress": f"{min(100, exp_progress * 100):.0f}%",
        }

    def get_status_display(self) -> str:
        """Get a compact status string for the console UI."""
        progress = self.get_progress()
        return (
            f"Lv.{self._level} {self.level_name} | "
            f"Vocab: {progress.get('vocabulary', '?')} | "
            f"Exp: {progress.get('experiences', '?')}"
        )

    # ─── Persistence ─────────────────────────────────────────

    def _save_level(self) -> None:
        self._memory.save_state("growth_level", str(self._level))
        self._memory.save_state("capabilities", json.dumps(self._capabilities))

    def _load_level(self) -> int:
        saved = self._memory.load_state("growth_level", "0")
        try:
            return int(saved)
        except ValueError:
            return 0
