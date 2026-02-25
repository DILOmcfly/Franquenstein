"""Pattern recognition — detects recurring structures in interactions.

Starts simple (word frequency, bigrams, response patterns) and can
evolve to more sophisticated methods as the being grows. No heavy ML
frameworks — just statistics and smart counting.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pattern:
    """A detected pattern."""

    id: Optional[int] = None
    pattern_type: str = ""
    pattern_key: str = ""
    pattern_value: dict = field(default_factory=dict)
    frequency: int = 1
    confidence: float = 0.1
    first_seen: str = ""
    last_seen: str = ""


class PatternDetector:
    """Detects and tracks patterns in the being's interactions.

    Pattern types:
        - word_freq: How often each word appears
        - bigram: Pairs of consecutive words that co-occur
        - response_pattern: Input→Output mappings that work well
        - topic: Clusters of related words that appear together
    """

    def __init__(self, db_connection: sqlite3.Connection):
        self._conn = db_connection

    # ─── Observe & Detect ────────────────────────────────────

    def observe(self, text: str) -> list[Pattern]:
        """Process a text input and update all pattern trackers.

        Returns newly significant patterns (those crossing
        the confidence threshold for the first time).
        """
        words = self._tokenize(text)
        new_patterns: list[Pattern] = []

        # Track word frequencies
        for word in words:
            pattern = self._record_pattern("word_freq", word)
            if pattern and pattern.frequency == 3:  # First time becoming "known"
                new_patterns.append(pattern)

        # Track bigrams (word pairs)
        for i in range(len(words) - 1):
            bigram = f"{words[i]}_{words[i+1]}"
            pattern = self._record_pattern("bigram", bigram)
            if pattern and pattern.frequency == 3:
                new_patterns.append(pattern)

        return new_patterns

    def observe_response(
        self,
        input_text: str,
        output_text: str,
        feedback_score: float = 0.0,
    ) -> Optional[Pattern]:
        """Track an input→output pair with its effectiveness.

        If feedback is positive, the response pattern strengthens.
        If negative, it weakens.
        """
        key = self._normalize(input_text)
        existing = self._get_pattern("response_pattern", key)

        if existing:
            # Update existing response pattern
            value = existing.pattern_value
            responses = value.get("responses", [])

            # Add or update this response
            found = False
            for resp in responses:
                if resp["output"] == output_text:
                    resp["score"] = (resp["score"] * 0.7) + (feedback_score * 0.3)
                    resp["count"] += 1
                    found = True
                    break

            if not found:
                responses.append({
                    "output": output_text,
                    "score": feedback_score,
                    "count": 1,
                })

            # Sort by score + repeat count (prefer stable responses)
            responses.sort(
                key=lambda r: (round(float(r["score"]), 3), int(r.get("count", 0))),
                reverse=True,
            )
            value["responses"] = responses[:5]  # Keep top 5

            self._update_pattern(
                "response_pattern",
                key,
                value,
                confidence=max(r["score"] for r in responses) if responses else 0.1,
            )
            return self._get_pattern("response_pattern", key)
        else:
            # New response pattern
            value = {
                "responses": [{
                    "output": output_text,
                    "score": feedback_score,
                    "count": 1,
                }]
            }
            return self._record_pattern(
                "response_pattern",
                key,
                value,
            )

    # ─── Query ───────────────────────────────────────────────

    def get_best_response(self, input_text: str) -> Optional[str]:
        """Get the best known response for an input (if any).

        Returns the highest-scored response pattern, or None
        if no good pattern exists.
        """
        key = self._normalize(input_text)
        pattern = self._get_pattern("response_pattern", key)

        if not pattern:
            return None

        responses = pattern.pattern_value.get("responses", [])
        if not responses:
            return None

        # Prefer stable responses (count>=2) with positive score.
        stable = [
            r for r in responses
            if float(r.get("score", 0.0)) > 0.0 and int(r.get("count", 0)) >= 2
        ]
        if stable:
            stable.sort(
                key=lambda r: (round(float(r["score"]), 3), int(r.get("count", 0))),
                reverse=True,
            )
            return stable[0]["output"]

        # Fallback: allow high-confidence single-shot answers only if very strong.
        best = responses[0]
        if float(best.get("score", 0.0)) >= 0.9:
            return best["output"]
        return None

    def get_known_words(self, min_frequency: int = 3) -> list[tuple[str, int]]:
        """Get words the being 'knows' (has seen multiple times)."""
        rows = self._conn.execute(
            """
            SELECT pattern_key, frequency FROM patterns
            WHERE pattern_type = 'word_freq' AND frequency >= ?
            ORDER BY frequency DESC
            """,
            (min_frequency,),
        ).fetchall()
        return [(row[0], row[1]) for row in rows]

    def get_top_patterns(
        self,
        pattern_type: str = "word_freq",
        limit: int = 20,
    ) -> list[Pattern]:
        """Get the most frequent patterns of a given type."""
        rows = self._conn.execute(
            """
            SELECT * FROM patterns
            WHERE pattern_type = ?
            ORDER BY frequency DESC
            LIMIT ?
            """,
            (pattern_type, limit),
        ).fetchall()
        return [self._row_to_pattern(row) for row in rows]

    def get_word_count(self) -> int:
        """Total unique words observed."""
        row = self._conn.execute(
            "SELECT COUNT(*) FROM patterns WHERE pattern_type = 'word_freq'"
        ).fetchone()
        return row[0] if row else 0

    # ─── Internal ────────────────────────────────────────────

    def _record_pattern(
        self,
        pattern_type: str,
        pattern_key: str,
        pattern_value: Optional[dict] = None,
    ) -> Optional[Pattern]:
        """Record or increment a pattern."""
        existing = self._get_pattern(pattern_type, pattern_key)

        if existing:
            new_freq = existing.frequency + 1
            new_conf = min(1.0, 0.1 + (new_freq * 0.05))
            self._conn.execute(
                """
                UPDATE patterns
                SET frequency = ?, confidence = ?, last_seen = datetime('now')
                WHERE pattern_type = ? AND pattern_key = ?
                """,
                (new_freq, new_conf, pattern_type, pattern_key),
            )
            self._conn.commit()
            existing.frequency = new_freq
            existing.confidence = new_conf
            return existing
        else:
            value_json = json.dumps(pattern_value or {})
            self._conn.execute(
                """
                INSERT INTO patterns (pattern_type, pattern_key, pattern_value)
                VALUES (?, ?, ?)
                """,
                (pattern_type, pattern_key, value_json),
            )
            self._conn.commit()
            return self._get_pattern(pattern_type, pattern_key)

    def _update_pattern(
        self,
        pattern_type: str,
        pattern_key: str,
        pattern_value: dict,
        confidence: float = 0.1,
    ) -> None:
        """Update an existing pattern's value and confidence."""
        self._conn.execute(
            """
            UPDATE patterns
            SET pattern_value = ?, confidence = ?,
                frequency = frequency + 1, last_seen = datetime('now')
            WHERE pattern_type = ? AND pattern_key = ?
            """,
            (json.dumps(pattern_value), confidence, pattern_type, pattern_key),
        )
        self._conn.commit()

    def _get_pattern(self, pattern_type: str, pattern_key: str) -> Optional[Pattern]:
        """Retrieve a specific pattern."""
        row = self._conn.execute(
            """
            SELECT * FROM patterns
            WHERE pattern_type = ? AND pattern_key = ?
            """,
            (pattern_type, pattern_key),
        ).fetchone()
        return self._row_to_pattern(row) if row else None

    # ─── Helpers ─────────────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Simple tokenizer: lowercase, strip punctuation, filter short words."""
        words = text.lower().split()
        cleaned: list[str] = []
        for w in words:
            w = w.strip(".,!?¿¡;:\"'()[]{}—–-")
            if len(w) > 1:  # Keep words with at least 2 chars
                cleaned.append(w)
        return cleaned

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for pattern matching."""
        return text.lower().strip()

    @staticmethod
    def _row_to_pattern(row: tuple) -> Pattern:
        value: dict = {}
        try:
            value = json.loads(row[3]) if row[3] else {}
        except (json.JSONDecodeError, TypeError):
            pass

        return Pattern(
            id=row[0],
            pattern_type=row[1],
            pattern_key=row[2],
            pattern_value=value,
            frequency=row[4],
            confidence=row[5],
            first_seen=row[6],
            last_seen=row[7],
        )
