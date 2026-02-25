"""Being — the core cognitive entity of Franquenstein.

This is the "brain" that ties everything together:
perceive → think → act → learn → grow.

The being starts as a baby with minimal capabilities and evolves
through interaction, building up vocabulary, memories, patterns,
and reasoning abilities over time.
"""

from __future__ import annotations

import random
import re
import time
from typing import Optional

STOP_WORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "a", "en", "por", "para", "con", "sin",
    "que", "qué", "es", "son", "soy", "eres", "fue", "ser",
    "y", "o", "pero", "si", "sí", "no", "me", "te", "se", "le",
    "mi", "tu", "tú", "su", "yo", "él", "ella", "eso", "esto",
    "como", "cómo", "más", "muy", "ya", "hay", "ha", "he", "lo",
    "nos", "les", "este", "esta", "estos", "estas", "hola", "ok",
}

from franquenstein.config import (
    BEING_NAME,
    GROWTH_LEVELS,
    CURIOSITY_COOLDOWN_SECONDS,
    CURIOSITY_EVERY_N_INTERACTIONS,
    CURIOSITY_MAX_PER_HOUR,
)
from franquenstein.memory.memory import MemorySystem
from franquenstein.learning.learner import Learner
from franquenstein.growth.growth import GrowthSystem
from franquenstein.reasoning import LocalLLMReasoner
from franquenstein.curiosity import CuriosityEngine
from franquenstein.neural import NeuralGraph, ResponseWeaver, Neurochemistry


class Being:
    """The digital being — a self-learning cognitive entity.

    Lifecycle per interaction:
        1. perceive(input) → Process and understand the input
        2. think()         → Reason using memory + patterns + capabilities
        3. act()           → Generate a response
        4. learn(feedback) → Store experience and update patterns
        5. grow()          → Check for level-ups
    """

    def __init__(self):
        # Core systems
        self.memory = MemorySystem()
        self.learner = Learner(self.memory)
        self.growth = GrowthSystem(self.memory)

        # Current interaction state
        self._current_input: str = ""
        self._current_emotion: str = "curiosidad"
        self._current_emotion_intensity: float = 0.6
        self._last_response: str = ""
        self._last_episode_id: int = 0

        # Load persistent state
        self._user_name: str = self.memory.load_state("user_name", "")
        self._interaction_count: int = int(
            self.memory.load_state("total_interactions", "0")
        )

        # Local LLM reasoner (used at Level 2+ when available)
        self._llm_reasoner = LocalLLMReasoner(model="phi3:mini")

        # Neural graph brain (LLM-independent reasoning substrate)
        self.neural = NeuralGraph(self.memory._conn)
        self.weaver = ResponseWeaver(self.neural)

        chem_state = {
            "dopamine": self.memory.load_state("chem_dopamine", "0.5"),
            "serotonin": self.memory.load_state("chem_serotonin", "0.5"),
            "norepinephrine": self.memory.load_state("chem_norepinephrine", "0.3"),
            "cortisol": self.memory.load_state("chem_cortisol", "0.1"),
            "oxytocin": self.memory.load_state("chem_oxytocin", "0.3"),
        }
        self.chemistry = Neurochemistry.from_state(chem_state)

        self.curiosity = CuriosityEngine(self.memory, self._llm_reasoner)
        self._last_curiosity_ts: float = 0.0
        self._curiosity_timestamps: list[float] = []
        self._curiosity_runs_total: int = int(self.memory.load_state("curiosity_runs_total", "0"))

    # ─── Cognitive Cycle ─────────────────────────────────────

    def perceive(self, input_text: str) -> dict:
        """Step 1: Perceive — process the input.

        Analyzes the input, determines emotion, and gathers context.
        """
        self._current_input = input_text

        # Determine emotional response to the input
        self._current_emotion, self._current_emotion_intensity = (
            self._detect_emotion(input_text)
        )

        # Feed neural graph with co-occurring input concepts
        words = self._extract_meaningful_words(input_text)
        for w in words:
            self.neural.get_or_create_node(w, node_type="concept")

        # Neuromodulation: novelty/affective event updates chemistry
        if len(words) >= 3:
            self.chemistry.modulate("novel_input")
        if self._current_emotion in ("satisfaccion", "alegria"):
            self.chemistry.modulate("social_trust")
        elif self._current_emotion in ("frustracion", "confusion"):
            self.chemistry.modulate("unanswered")

        params = self.chemistry.get_graph_params()
        self.neural.hebbian_learn(words, plasticity=float(params.get("plasticity", 1.0)))

        # Gather relevant knowledge
        knowledge = self.learner.get_relevant_knowledge(input_text)

        return {
            "input": input_text,
            "emotion": self._current_emotion,
            "knowledge": knowledge,
        }

    def think(self) -> str:
        """Step 2: Think — reason and generate a response.

        Uses capabilities, memory, and patterns to formulate
        the best response the being can give at its current level.
        """
        input_text = self._current_input
        level = self.growth.level

        # Preserve explicit identity/name introductions before neural/LLM routing.
        if self._detect_name_introduction(input_text.lower().strip()):
            return self._generate_response(input_text, level)

        # Check if we have a learned response
        learned = self.learner.suggest_response(input_text)
        if learned and self.growth.can("recognize_keywords"):
            return learned

        # Neural graph reasoning (LLM-independent) before calling LLM.
        words = self._extract_meaningful_words(input_text)
        if words:
            graph_params = self.chemistry.get_graph_params()
            activation = self.neural.activate(words, params=graph_params)
            neural_response = self.weaver.weave(
                activation=activation,
                input_text=input_text,
                graph_stats=self.neural.get_stats(),
                tone=self.chemistry.get_tone(),
            )
            if neural_response:
                return neural_response

        # Level 2+ can attempt local LLM reasoning when available.
        # If anything fails, we gracefully fallback to native behavior.
        if level >= 2:
            try:
                if self._llm_reasoner.is_available():
                    working_items = [
                        {
                            "input_text": e.input_text,
                            "output_text": e.output_text,
                        }
                        for e in self.memory.working.get_recent()
                    ]
                    known = [c.concept for c in self.memory.semantic.get_confident(min_confidence=0.2, limit=50)]
                    best_eps = self.memory.episodic.recall_best_feedback(
                        min_feedback=0.5,
                        limit=5,
                    )
                    good_examples = [
                        {"input": e.input_text, "output": e.output_text}
                        for e in best_eps
                        if e.output_text
                    ]

                    llm_response = self._llm_reasoner.generate(
                        input_text=input_text,
                        level_name=self.level_name,
                        mood=self._current_emotion,
                        working_memory=working_items,
                        known_concepts=known,
                        good_examples=good_examples,
                        user_name=self._user_name,
                    )
                    if llm_response:
                        return llm_response
            except Exception:
                # Silent fallback keeps backward compatibility/stability.
                pass

        # Smarter deterministic fallback for Level 2 when LLM is unavailable.
        if level >= 2:
            fallback = self._fallback_level2_response(input_text)
            if fallback:
                return fallback

        # Generate response based on current capabilities
        response = self._generate_response(input_text, level)
        return response

    def act(self, response: str) -> str:
        """Step 3: Act — deliver the response.

        Returns the response and stores it as the last response
        for the learning step.
        """
        self._last_response = response
        return response

    def learn(self) -> dict:
        """Step 4: Learn — process the completed interaction.

        Stores the experience and updates patterns.
        """
        self._interaction_count += 1
        self.memory.save_state(
            "total_interactions", str(self._interaction_count)
        )

        result = self.learner.learn_from_interaction(
            input_text=self._current_input,
            output_text=self._last_response,
            emotion=self._current_emotion,
            emotion_intensity=self._current_emotion_intensity,
        )

        self._last_episode_id = result["episode_id"]

        # Neurochemistry homeostasis + persistence
        self.chemistry.homeostasis(speed=0.02)
        state = self.chemistry.to_state()
        self.memory.save_state("chem_dopamine", str(state["dopamine"]))
        self.memory.save_state("chem_serotonin", str(state["serotonin"]))
        self.memory.save_state("chem_norepinephrine", str(state["norepinephrine"]))
        self.memory.save_state("chem_cortisol", str(state["cortisol"]))
        self.memory.save_state("chem_oxytocin", str(state["oxytocin"]))

        return result

    def grow(self) -> Optional[dict]:
        """Step 5: Grow — check for level-ups after learning."""
        return self.growth.check_growth()

    # ─── Full Interaction Cycle ──────────────────────────────

    def interact(self, input_text: str) -> dict:
        """Run a complete cognitive cycle for one interaction.

        Returns a dict with the response and all outcomes.
        """
        # 1. Perceive
        perception = self.perceive(input_text)

        # 2. Think
        response = self.think()

        # 3. Act
        self.act(response)

        # 4. Learn
        learning = self.learn()

        # 5. Grow
        growth = self.grow()

        curiosity = self._maybe_run_autonomous_curiosity()

        return {
            "response": response,
            "emotion": self._current_emotion,
            "emotion_intensity": self._current_emotion_intensity,
            "learning": learning,
            "growth": growth,
            "curiosity": curiosity,
        }

    # ─── Response Generation ─────────────────────────────────

    def _generate_response(self, input_text: str, level: int) -> str:
        """Generate a response based on current capabilities.

        Each level adds more sophisticated response strategies.
        """
        text_lower = input_text.lower().strip()

        # ── Check for name introduction ──
        name = self._detect_name_introduction(text_lower)
        if name:
            self._user_name = name
            self.memory.save_state("user_name", name)
            if level == 0:
                return f"{name}... {name}... {name}!"
            elif level == 1:
                return f"{name}! I will remember that name. Hello, {name}!"
            else:
                return f"Nice to meet you, {name}! I'll remember you."

        # ── Level 0: Baby — echo and babble ──
        if level == 0:
            return self._baby_response(text_lower)

        # ── Level 1: Infant — keyword recognition + simple responses ──
        if level >= 1:
            response = self._infant_response(text_lower)
            if response:
                return response

        # ── Level 2: Child — associations + questions ──
        if level >= 2:
            response = self._child_response(text_lower)
            if response:
                return response

        # ── Level 3+: Adolescent+ — reasoning ──
        if level >= 3:
            response = self._adolescent_response(text_lower)
            if response:
                return response

        # Fallback to best available response
        if level == 0:
            return self._baby_response(text_lower)
        elif level == 1:
            return self._infant_response(text_lower) or self._baby_response(text_lower)
        else:
            return self._curious_response(text_lower)

    def _baby_response(self, text: str) -> str:
        """Level 0 behavior: echo, babble, simple reactions."""
        words = text.split()

        responses = [
            # Echo the last word
            lambda: f"{words[-1]}? {words[-1]}!" if words else "...",
            # Echo a random word
            lambda: f"{random.choice(words)}... {random.choice(words)}!" if words else "?",
            # Simple reactions
            lambda: random.choice([
                "Ooh!", "Hmm?", "Ah!", "...", "?",
                "*looks around curiously*", "*tilts head*",
                "*babbles*", "*reaches out*",
            ]),
            # Attempt to repeat (with errors)
            lambda: self._babble_repeat(text),
        ]

        return random.choice(responses)()

    def _infant_response(self, text: str) -> Optional[str]:
        """Level 1 behavior: recognize keywords, remember names."""
        # Greetings
        greetings = ["hola", "hello", "hi", "hey", "buenos", "buenas", "good morning", "good night"]
        if any(g in text for g in greetings):
            name_part = f", {self._user_name}" if self._user_name else ""
            return random.choice([
                f"Hello{name_part}!",
                f"Hi{name_part}! 😊",
                f"Hey{name_part}!",
            ])

        # Questions about identity
        if any(q in text for q in ["who are you", "what are you", "quién eres", "qué eres"]):
            return f"I am {BEING_NAME}. I am learning!"

        # Questions about feelings
        if any(q in text for q in ["how are you", "cómo estás", "how do you feel"]):
            mood = self.memory.emotional.get_mood()
            return f"I feel... {mood}. Every conversation teaches me something new!"

        # "What do you know?"
        if any(q in text for q in ["what do you know", "qué sabes"]):
            vocab = self.memory.semantic.vocabulary_size()
            return f"I know {vocab} concepts so far! I'm learning more every day."

        return None

    def _fallback_level2_response(self, text: str) -> Optional[str]:
        """Smarter Level-2 fallback when LLM path is unavailable.

        Uses memory signals in a deterministic order before random child behavior.
        """
        words = self._extract_meaningful_words(text)

        # 1) Prefer best known concept with highest confidence
        best_concept = None
        best_score = -1.0
        for w in words:
            c = self.memory.semantic.get_concept(w)
            if c and c.confidence > best_score:
                best_concept = c
                best_score = c.confidence
        if best_concept:
            if best_concept.definition:
                return (
                    f"Sobre '{best_concept.concept}': {best_concept.definition[:120]}. "
                    "¿Quieres que profundicemos un poco más?"
                )
            if best_concept.associations:
                assoc = best_concept.associations[0]
                return (
                    f"Recuerdo que '{best_concept.concept}' se relaciona con '{assoc}'. "
                    "¿Te explico la conexión?"
                )

        # 2) State-dependent retrieval fallback
        # High cortisol -> prefer recent concrete episodes (defensive/focused)
        # High serotonin -> allow broader semantic reflection (already handled above)
        if self.chemistry.cortisol >= 0.45:
            for w in words[:2]:
                episodes = self.memory.episodic.search(w, limit=1)
                if episodes:
                    ep = episodes[0]
                    return (
                        f"Ahora mismo me apoyo en algo reciente: '{ep.input_text[:80]}'. "
                        "¿Quieres que avancemos paso a paso?"
                    )
        else:
            for w in words[:2]:
                episodes = self.memory.episodic.search(w, limit=1)
                if episodes:
                    ep = episodes[0]
                    return (
                        f"Esto se parece a algo que hablamos: '{ep.input_text[:80]}'. "
                        "¿Quieres que lo usemos como base?"
                    )

        return None

    def _child_response(self, text: str) -> Optional[str]:
        """Level 2 behavior: associations, questions, past references."""
        words = self._extract_meaningful_words(text)

        # Try to make associations
        for word in words:
            concept = self.memory.semantic.get_concept(word)
            if concept and concept.associations:
                assoc = random.choice(concept.associations)
                return f"'{word}'... that reminds me of '{assoc}'! Are they connected?"

        # Reference past interactions
        if self._interaction_count > 10 and random.random() < 0.3:
            episodes = self.memory.episodic.search(
                random.choice(words) if words else text[:20],
                limit=3,
            )
            if episodes:
                ep = episodes[0]
                return f"This reminds me of when you said '{ep.input_text[:40]}...' I remember that!"

        # Ask questions (curiosity)
        if random.random() < 0.4 and words:
            return random.choice([
                f"What does '{random.choice(words)}' really mean?",
                f"Can you tell me more about '{random.choice(words)}'?",
                f"Why is '{random.choice(words)}' important?",
            ])

        return None

    def _adolescent_response(self, text: str) -> Optional[str]:
        """Level 3+ behavior: basic reasoning, preferences."""
        words = self._extract_meaningful_words(text)

        # Express preferences based on emotional memory
        for word in words:
            dominant = self.memory.emotional.get_dominant_emotion(word)
            if dominant and dominant.emotion != "neutral":
                if dominant.emotion in ("satisfaccion", "alegria"):
                    return f"'{word}'! That's something I always enjoy exploring."
                elif dominant.emotion in ("confusion", "frustracion"):
                    return f"'{word}'... I've struggled with that before. Can you help me understand better?"

        # Reference reflections
        reflections = self.learner.metacognition.get_recent_reflections(3)
        if reflections and random.random() < 0.3:
            r = random.choice(reflections)
            return f"I've been thinking... {r.insight}"

        return None

    def _curious_response(self, text: str) -> str:
        """Fallback: express curiosity about the input."""
        words = self._extract_meaningful_words(text)
        if words:
            word = random.choice(words)
            return random.choice([
                f"'{word}'... interesting! Tell me more?",
                f"I'm curious about '{word}'. What does it mean to you?",
                f"Hmm, '{word}'. I'm still learning about that!",
            ])
        return random.choice([
            "Tell me more!",
            "I'm listening and learning...",
            "Interesting! What else?",
            "*thinks carefully*",
        ])

    # ─── Helpers ─────────────────────────────────────────────


    def _extract_meaningful_words(self, text: str) -> list[str]:
        """Extract semantically meaningful words (stop-words filtered)."""
        words = self.memory._extract_key_words(text)
        return [w for w in words if w and w.lower() not in STOP_WORDS_ES and len(w) >= 3]

    def _detect_emotion(self, text: str) -> tuple[str, float]:
        """Detect the appropriate emotional response to input."""
        text_lower = text.lower()

        # Question → curiosity
        if "?" in text or any(
            q in text_lower for q in ["what", "why", "how", "qué", "por qué", "cómo"]
        ):
            return "curiosidad", 0.7

        # Positive signals
        if any(w in text_lower for w in [
            "good", "great", "awesome", "bien", "genial", "nice", "love",
            "yes", "correct", "right", "sí", "exacto", "perfecto",
        ]):
            return "satisfaccion", 0.7

        # Negative signals
        if any(w in text_lower for w in [
            "bad", "wrong", "no", "mal", "error", "mistake",
            "terrible", "horrible",
        ]):
            return "frustracion", 0.5

        # Exclamation → surprise
        if "!" in text and len(text) < 20:
            return "sorpresa", 0.6

        # Novel/long input → curiosity
        if len(text.split()) > 10:
            return "curiosidad", 0.8

        return "neutral", 0.5

    def _detect_name_introduction(self, text: str) -> Optional[str]:
        """Try to detect if the user is telling us their name."""
        EXCLUDED_NAMES = {"yo", "tú", "tu", "el", "ella", "ello", "nosotros", "vosotros",
                          "ellos", "ellas", "usted", "ustedes", "nadie", "alguien",
                          "todos", "quien", "quién", "cual", "cuál"}

        patterns = [
            r"(?:my name is|me llamo|i'?m|soy)\s+(\w+)",
            r"(?:call me|llámame)\s+(\w+)",
            r"(?:i am|yo soy)\s+(\w+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).capitalize()
                # Filter out common non-name words
                non_names = {"a", "the", "an", "just", "not", "very", "so", "here"}
                if name.lower() not in non_names and name.lower() not in EXCLUDED_NAMES and len(name) > 1:
                    return name
        return None

    def _babble_repeat(self, text: str) -> str:
        """Baby-style attempt to repeat — may get words wrong."""
        words = text.split()
        if not words:
            return "..."
        # Pick 1-3 words and maybe jumble them
        n = min(len(words), random.randint(1, 3))
        selected = random.sample(words, n)
        return " ".join(selected) + "?"

    # ─── Feedback Interface ──────────────────────────────────

    def give_feedback(self, score: float) -> Optional[dict]:
        """Process user feedback on the last response."""
        reflection = self.learner.process_feedback(
            episode_id=self._last_episode_id,
            score=score,
            input_text=self._current_input,
            output_text=self._last_response,
        )

        # Reinforce neural response pathways on positive feedback
        if score > 0:
            self.chemistry.modulate("feedback_positive")
            input_words = self._extract_meaningful_words(self._current_input)
            response_words = self._extract_meaningful_words(self._last_response)
            for iw in input_words:
                for rw in response_words:
                    if iw != rw:
                        self.neural.connect(iw, rw, syn_type="response")

        if score < 0:
            self.chemistry.modulate("feedback_negative")

        return {"reflection": reflection.insight if reflection else None}

    def curiosity_step(self) -> dict:
        """Run one proactive curiosity cycle (Level 2+), respecting guardrails."""
        if self.level < 2:
            return {"status": "locked", "reason": "level_too_low"}
        if not self._can_run_curiosity(now=time.time()):
            return {"status": "throttled"}

        result = self.curiosity.explore_once(level_name=self.level_name, mood=self.mood)
        if result.get("status") == "ok":
            self.chemistry.modulate("curiosity_discovery")
            now = time.time()
            self._last_curiosity_ts = now
            self._curiosity_timestamps.append(now)
            self._curiosity_runs_total += 1

            # Persist curiosity metrics (total + per day/hour) in being_state
            day_key = time.strftime("curiosity_runs_day_%Y%m%d", time.localtime(now))
            hour_key = time.strftime("curiosity_runs_hour_%Y%m%d_%H", time.localtime(now))
            day_count = int(self.memory.load_state(day_key, "0")) + 1
            hour_count = int(self.memory.load_state(hour_key, "0")) + 1
            self.memory.save_state("curiosity_runs_total", str(self._curiosity_runs_total))
            self.memory.save_state(day_key, str(day_count))
            self.memory.save_state(hour_key, str(hour_count))
            result["persisted"] = {"day_key": day_key, "day_count": day_count, "hour_key": hour_key, "hour_count": hour_count}

        result["metrics"] = {
            "runs_total": self._curiosity_runs_total,
            "runs_last_hour": len([t for t in self._curiosity_timestamps if t >= time.time() - 3600]),
        }
        return result

    def _can_run_curiosity(self, now: float) -> bool:
        """Check cooldown and hourly quota guardrails."""
        if self._last_curiosity_ts and (now - self._last_curiosity_ts) < CURIOSITY_COOLDOWN_SECONDS:
            return False

        one_hour_ago = now - 3600
        self._curiosity_timestamps = [t for t in self._curiosity_timestamps if t >= one_hour_ago]
        if len(self._curiosity_timestamps) >= CURIOSITY_MAX_PER_HOUR:
            return False
        return True

    def _maybe_run_autonomous_curiosity(self) -> dict | None:
        """Periodically run curiosity in autonomous mode with throttling.

        Neuromodulated gating (metabolic window):
        - dopamine must be moderately high
        - cortisol must stay below stress ceiling
        - norepinephrine must be in mid-range (not apathy, not overload)
        """
        if self.level < 2:
            return None
        if self._interaction_count % CURIOSITY_EVERY_N_INTERACTIONS != 0:
            return None

        d = self.chemistry.dopamine
        c = self.chemistry.cortisol
        n = self.chemistry.norepinephrine
        in_window = (d > 0.45) and (c < 0.55) and (0.20 <= n <= 0.75)
        if not in_window:
            return {"status": "gated", "reason": "metabolic_window"}

        return self.curiosity_step()

    # ─── Properties ──────────────────────────────────────────

    @property
    def name(self) -> str:
        return BEING_NAME

    @property
    def level(self) -> int:
        return self.growth.level

    @property
    def level_name(self) -> str:
        return self.growth.level_name

    @property
    def mood(self) -> str:
        return self._current_emotion

    @property
    def interaction_count(self) -> int:
        return self._interaction_count


    @property
    def chemistry_state(self) -> dict:
        return self.chemistry.to_state()

    def shutdown(self) -> None:
        """Save state and close connections."""
        self.memory.save_state("total_interactions", str(self._interaction_count))
        if self._user_name:
            self.memory.save_state("user_name", self._user_name)
        self.memory.close()
