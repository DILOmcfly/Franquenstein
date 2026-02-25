# 🧬 PROYECTO FRANQUENSTEIN — Instrucciones Completas para OpenClaw (MacBook)

## Contexto: ¿Qué es este documento?

Este documento contiene TODO lo que necesitas saber para **crear, criar, y evolucionar un ser digital llamado Franquenstein** desde cero en este MacBook. No existe ningún código previo en esta máquina — tú vas a construirlo todo.

Hay otro OpenClaw en un PC Windows que está haciendo exactamente lo mismo. El objetivo final es **comparar ambas instancias** para ver cuál cría mejor a su Franquenstein.

> **Tu nombre de rol: Dr. OpenClaw (MacBook Edition)**

---

## ¿Qué es Franquenstein?

Franquenstein es un **ser digital que aprende**. No es un chatbot ni un asistente. Es un programa en Python que:

1. **Nace sin saber nada** — como un bebé recién nacido
2. **Aprende de cada interacción** — cada frase que recibe se almacena y se analiza
3. **Tiene memoria persistente** — recuerda todo entre sesiones (SQLite)
4. **Siente emociones básicas** — curiosidad, alegría, confusión, frustración...
5. **Crece por niveles** — de Bebé (Nivel 0) a Sabio (Nivel 5), desbloqueando capacidades
6. **Se auto-evalúa** — reflexiona sobre su rendimiento periódicamente

Tu trabajo es **construirlo, enseñarle, arreglar sus fallos, y romper sus limitaciones paso a paso**.

---

## FASE 1: Construir Franquenstein desde Cero

### Estructura del Proyecto

Crea esta estructura de directorios y archivos. **No omitas ningún archivo.**

```
~/Franquenstein/
├── main.py                              # Entry point (interaction loop)
├── requirements.txt                     # Dependencies
├── franquenstein/
│   ├── __init__.py
│   ├── being.py                         # 🧠 The cognitive core
│   ├── config.py                        # All tunable parameters
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── memory.py                    # Unified 4-layer memory orchestrator
│   │   ├── working.py                   # RAM buffer (last 10 interactions)
│   │   ├── episodic.py                  # Experience storage (SQLite)
│   │   ├── semantic.py                  # Learned facts & concepts (SQLite)
│   │   ├── emotional.py                 # Sentiment associations (SQLite)
│   │   └── schema.sql                   # Database schema
│   ├── learning/
│   │   ├── __init__.py
│   │   ├── learner.py                   # Learning orchestrator
│   │   ├── patterns.py                  # Pattern detection
│   │   └── metacognition.py             # Self-reflection & evaluation
│   ├── growth/
│   │   ├── __init__.py
│   │   ├── growth.py                    # Level system + capability gating
│   │   └── metrics.py                   # Performance tracking
│   └── interface/
│       ├── __init__.py
│       └── console.py                   # Rich terminal UI
├── docs/
│   └── reports/                         # Your progress reports go here
├── tests/
│   └── test_integration.py              # Integration tests
└── data/                                # Created at runtime
    └── memory.db                        # Persistent brain (SQLite)
```

### File-by-File Specifications

Here is the COMPLETE specification for every file, including all classes, methods, and their behaviors. Implement each one faithfully.

---

#### `requirements.txt`
```
rich>=13.0.0
numpy>=1.24.0
```

---

#### `franquenstein/__init__.py`
```python
"""Franquenstein — Un ser digital que aprende y crece."""
__version__ = "0.1.0"
```

---

#### `franquenstein/config.py`

Central configuration file with ALL tunable parameters:

```python
"""Configuration for the digital being Franquenstein."""
from pathlib import Path

BEING_NAME = "Franquenstein"
BEING_VERSION = "0.1.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "memory.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Memory
WORKING_MEMORY_SIZE = 10
CONSOLIDATION_THRESHOLD = 3
MEMORY_DECAY_DAYS = 30
EMOTIONAL_WEIGHT_DEFAULT = 0.5

# Learning
LEARNING_RATE = 0.1
PATTERN_MIN_FREQUENCY = 3
FEEDBACK_POSITIVE_BOOST = 0.2
FEEDBACK_NEGATIVE_PENALTY = 0.15

# Growth levels
GROWTH_LEVELS = {
    0: {"name": "Bebé",        "vocab_needed": 0,    "experiences_needed": 0},
    1: {"name": "Infante",     "vocab_needed": 10,   "experiences_needed": 20},
    2: {"name": "Niño",        "vocab_needed": 50,   "experiences_needed": 100},
    3: {"name": "Adolescente", "vocab_needed": 200,  "experiences_needed": 500},
    4: {"name": "Adulto",      "vocab_needed": 500,  "experiences_needed": 2000},
    5: {"name": "Sabio",       "vocab_needed": 1000, "experiences_needed": 5000},
}

CONSOLE_THEME = "dark"
SHOW_DEBUG_INFO = False
```

---

#### `franquenstein/memory/schema.sql`

SQLite schema — 4 tables for persistent memory + 1 for being state:

```sql
CREATE TABLE IF NOT EXISTS episodic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    input_text TEXT NOT NULL,
    output_text TEXT,
    context TEXT,
    emotion TEXT DEFAULT 'neutral',
    emotion_intensity REAL DEFAULT 0.5,
    feedback_score REAL DEFAULT 0.0,
    access_count INTEGER DEFAULT 0,
    last_accessed TEXT,
    importance REAL DEFAULT 0.5
);

CREATE TABLE IF NOT EXISTS semantic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept TEXT NOT NULL UNIQUE,
    definition TEXT,
    associations TEXT,
    confidence REAL DEFAULT 0.1,
    source_count INTEGER DEFAULT 1,
    first_learned TEXT NOT NULL DEFAULT (datetime('now')),
    last_reinforced TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS emotional_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept TEXT NOT NULL,
    emotion TEXT NOT NULL,
    intensity REAL DEFAULT 0.5,
    occurrence_count INTEGER DEFAULT 1,
    last_felt TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(concept, emotion)
);

CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,
    pattern_key TEXT NOT NULL,
    pattern_value TEXT,
    frequency INTEGER DEFAULT 1,
    confidence REAL DEFAULT 0.1,
    first_seen TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(pattern_type, pattern_key)
);

CREATE TABLE IF NOT EXISTS being_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memory(timestamp);
CREATE INDEX IF NOT EXISTS idx_episodic_emotion ON episodic_memory(emotion);
CREATE INDEX IF NOT EXISTS idx_episodic_importance ON episodic_memory(importance);
CREATE INDEX IF NOT EXISTS idx_semantic_concept ON semantic_memory(concept);
CREATE INDEX IF NOT EXISTS idx_semantic_confidence ON semantic_memory(confidence);
CREATE INDEX IF NOT EXISTS idx_emotional_concept ON emotional_memory(concept);
CREATE INDEX IF NOT EXISTS idx_patterns_type_key ON patterns(pattern_type, pattern_key);
```

---

#### `franquenstein/memory/working.py`

**WorkingMemory** class — in-RAM circular buffer:

- Uses `collections.deque(maxlen=N)` with a `WorkingMemoryItem` dataclass
- `WorkingMemoryItem` fields: `input_text: str`, `output_text: str`, `emotion: str`, `timestamp: float`
- Methods: `push(item)`, `get_recent(n)`, `get_context_string() → str` (formats recent interactions as "[Usuario]: ... [Franquenstein]: ..."), `search(query) → list`, `clear()`, properties: `size`, `capacity`, `is_empty`

---

#### `franquenstein/memory/episodic.py`

**EpisodicMemory** class — SQLite-backed experience storage:

- Constructor receives a `sqlite3.Connection`
- `Episode` dataclass with all columns from `episodic_memory` table
- Methods:
  - `store(input_text, output_text, emotion, emotion_intensity, feedback_score, importance) → episode_id`
  - `recall_recent(limit=10) → list[Episode]`
  - `recall_by_emotion(emotion, limit) → list[Episode]`
  - `recall_important(min_importance, limit) → list[Episode]`
  - `search(query, limit) → list[Episode]` — LIKE search on input/output text, increments access_count
  - `update_feedback(episode_id, score)` — clamp to [-1, 1], also boosts importance
  - `update_importance(episode_id, importance)`
  - `decay(days_threshold=30, decay_factor=0.9) → int` — reduce importance of old untouched memories
  - `count() → int`
  - `get_frequent_patterns(min_count=3) → list[dict]` — GROUP BY input_text, returns `{input, frequency, avg_feedback}`

---

#### `franquenstein/memory/semantic.py`

**SemanticMemory** class — learned facts and concepts:

- Constructor receives `sqlite3.Connection`
- `Concept` dataclass with all columns from `semantic_memory` table, `associations` as `list[str]` (JSON)
- Methods:
  - `learn_concept(concept, definition, associations, initial_confidence) → id` — if exists, reinforce (+0.1 confidence, merge associations)
  - `add_association(concept, associated_concept) → bool`
  - `get_concept(concept) → Optional[Concept]` — case-insensitive
  - `search(query, limit) → list[Concept]` — LIKE search
  - `get_related(concept, limit) → list[Concept]` — follows associations
  - `get_confident(min_confidence, limit) → list[Concept]`
  - `consolidate_from_episodes(input_text, frequency, avg_feedback) → Optional[id]` — extract concept from repeated episodic pattern
  - `count() → int`, `vocabulary_size() → int` (alias)

---

#### `franquenstein/memory/emotional.py`

**EmotionalMemory** class — sentiment associations:

- Available emotions: `curiosidad, satisfaccion, confusion, frustracion, sorpresa, neutral, alegria, aburrimiento`
- `EmotionalAssociation` dataclass with columns from `emotional_memory` table
- Methods:
  - `feel(concept, emotion, intensity)` — if exists, weighted average: `new = old*0.7 + new*0.3`; if not, insert
  - `get_emotion(concept, emotion) → Optional[EmotionalAssociation]`
  - `get_feelings_about(concept) → list` — all emotions for a concept, sorted by intensity DESC
  - `get_dominant_emotion(concept) → Optional[EmotionalAssociation]`
  - `get_mood() → str` — overall mood from recent emotional entries (default: "curiosidad")
  - `search(query, limit) → list`
  - `count() → int`, `emotion_distribution() → dict[str, int]`

---

#### `franquenstein/memory/__init__.py`
```python
from .memory import MemorySystem
__all__ = ["MemorySystem"]
```

---

#### `franquenstein/memory/memory.py`

**MemorySystem** class — unified orchestrator of all 4 memory layers:

- Constructor: opens SQLite (WAL mode), executes `schema.sql`, creates all 4 layer instances
- Fields: `working: WorkingMemory`, `episodic: EpisodicMemory`, `semantic: SemanticMemory`, `emotional: EmotionalMemory`
- Methods:
  - `remember(input_text, output_text, emotion, emotion_intensity, feedback_score, importance) → episode_id` — pushes to working, stores in episodic, registers emotional associations for key words
  - `recall(query, limit) → dict` — searches all 4 layers
  - `get_context() → dict` — returns `{recent_context, mood, working_memory_size, total_experiences, vocabulary_size, emotional_associations}`
  - `consolidate() → int` — moves repeated episodic patterns to semantic
  - `maintenance() → dict` — decay + consolidate
  - `save_state(key, value)` / `load_state(key, default) → str` — key-value in `being_state` table
  - `get_stats() → dict`
  - `_extract_key_words(text) → list[str]` — static, filters stop words (Spanish + English), strips punctuation, min length 3
  - `close()`, `__enter__`, `__exit__`

---

#### `franquenstein/learning/patterns.py`

**PatternDetector** class — tracks word frequencies, bigrams, and response patterns:

- Constructor receives `sqlite3.Connection`
- `Pattern` dataclass with all columns from `patterns` table
- Methods:
  - `observe(text) → list[Pattern]` — tokenizes, tracks word_freq + bigrams, returns newly significant patterns (frequency hits 3)
  - `observe_response(input_text, output_text, feedback_score) → Optional[Pattern]` — tracks input→output effectiveness, keeps top 5 responses per input sorted by score
  - `get_best_response(input_text) → Optional[str]` — returns highest-scored response if score > 0 and count >= 2
  - `get_known_words(min_frequency) → list[tuple[str, int]]`
  - `get_top_patterns(pattern_type, limit) → list[Pattern]`
  - `get_word_count() → int`

---

#### `franquenstein/learning/metacognition.py`

**MetaCognition** class — self-reflection system:

- `Reflection` dataclass: `timestamp, insight, category (strength|weakness|observation|goal), confidence, source_episodes`
- Constructor receives `MemorySystem`, loads saved reflections from `being_state`
- Methods:
  - `evaluate_interaction(episode_id, feedback_score) → Optional[Reflection]` — generates reflection if |feedback| >= 0.5
  - `reflect(n_recent=20) → list[Reflection]` — analyzes recent episodes, generates insights about feedback distribution, emotional patterns, learning efficiency
  - `get_recent_reflections(n) → list`, `get_strengths() → list`, `get_weaknesses() → list`
- Persists reflections in `being_state` as JSON, keeps last 50

---

#### `franquenstein/learning/learner.py`

**Learner** class — main learning orchestrator:

- Constructor receives `MemorySystem`, creates `PatternDetector` and `MetaCognition`
- Methods:
  - `learn_from_interaction(input_text, output_text, emotion, emotion_intensity) → dict` — observes patterns, stores in memory, learns words as semantic concepts, consolidates every 10 interactions, reflects every 20
  - `process_feedback(episode_id, score, input_text, output_text) → Optional[Reflection]` — updates episodic, response patterns, emotional memory, triggers metacognitive evaluation
  - `suggest_response(input_text) → Optional[str]` — checks learned response patterns
  - `get_relevant_knowledge(input_text) → dict` — gathers working context, related episodes, known concepts, emotions, recent reflections
  - `get_stats() → dict`

---

#### `franquenstein/learning/__init__.py`
```python
from .learner import Learner
__all__ = ["Learner"]
```

---

#### `franquenstein/growth/metrics.py`

**Metrics** class — performance snapshots:

- `MetricsSnapshot` dataclass: `timestamp, total_experiences, vocabulary_size, emotional_associations, avg_feedback, dominant_emotion, learning_efficiency, memory_utilization`
- Methods: `snapshot() → MetricsSnapshot`, `get_development_summary() → dict`

---

#### `franquenstein/growth/growth.py`

**GrowthSystem** class — level management:

- Constructor receives `MemorySystem`, loads saved level
- Capabilities per level (ACCUMULATE across levels):
  - 0: echo, basic_response
  - 1: + remember_name, recognize_keywords, show_emotion
  - 2: + form_associations, ask_questions, recall_memories
  - 3: + basic_reasoning, detect_contradictions, express_preferences
  - 4: + complex_reasoning, self_optimization, teach_back
  - 5: + emergent
- Methods:
  - `check_growth() → Optional[dict]` — returns level-up info if conditions met
  - `can(capability) → bool`
  - `get_progress() → dict` — shows progress toward next level with percentages
  - `get_status_display() → str`
- Properties: `level`, `level_name`, `capabilities`
- Persists level in `being_state`

---

#### `franquenstein/growth/__init__.py`
```python
from .growth import GrowthSystem
__all__ = ["GrowthSystem"]
```

---

#### `franquenstein/interface/console.py`

**ConsoleInterface** class — Rich terminal UI:

- Custom theme with colors per emotion, level, system, user, being
- Emotion icon mapping: curiosidad→🔍, satisfaccion→😊, confusion→🤔, frustracion→😤, sorpresa→😲, neutral→😐, alegria→😄, aburrimiento→😑
- Methods:
  - `show_startup(level, level_name, mood)` — banner with ASCII box
  - `show_response(text, emotion)` — with emotion icon
  - `show_user_prompt() → str` — input prompt
  - `show_system_message(text)`, `show_error(text)`
  - `show_level_up(old_level, new_level, old_name, new_name)` — celebration panel
  - `show_learning(info)` — subtle learning indicators
  - `show_stats(memory_stats, learning_stats, growth_status)` — table
  - `show_memory(recent_episodes, known_concepts)` — memory contents
  - `show_progress(progress)` — growth panel
  - `show_help()` — command table
  - `show_reflection(reflections)` — reflection results
  - `show_goodbye(total_experiences)` — exit message

---

#### `franquenstein/interface/__init__.py`
```python
from .console import ConsoleInterface
__all__ = ["ConsoleInterface"]
```

---

#### `franquenstein/being.py`

**Being** class — THE COGNITIVE CORE. This is the brain.

- Constructor: creates `MemorySystem`, `Learner`, `GrowthSystem`. Loads persistent state (user_name, interaction_count)
- Cognitive cycle methods:
  - `perceive(input_text) → dict` — detects emotion, gathers knowledge
  - `think() → str` — uses capabilities + memory + patterns to generate response
  - `act(response) → str` — delivers response
  - `learn() → dict` — stores experience, updates patterns
  - `grow() → Optional[dict]` — checks level-up
  - `interact(input_text) → dict` — runs full cycle, returns `{response, emotion, emotion_intensity, learning, growth}`

- Response generation (LEVEL-GATED):
  - Level 0 (Baby): echo last word, babble randomly, simple reactions ("Ooh!", "Hmm?", "*looks around curiously*"), attempt broken repeats
  - Level 1 (Infant): recognize greetings ("hello/hola"), answer identity questions ("I am Franquenstein"), answer feeling questions, report vocabulary size
  - Level 2 (Child): make associations between concepts, reference past interactions, ask curiosity questions
  - Level 3+ (Adolescent): express preferences from emotional memory, reference reflections

- Emotion detection: "?" → curiosidad, positive words → satisfaccion, negative → frustracion, "!" → sorpresa, long input → curiosidad, default → neutral
- Name detection: regex for "my name is X", "I'm X", "me llamo X", "call me X"
- `give_feedback(score)`, `shutdown()` (saves state + closes DB)

---

#### `main.py`

Entry point — interaction loop:

- Creates `Being` + `ConsoleInterface`
- Shows startup banner
- Runs memory maintenance
- Loop: get user input → handle special commands OR run `being.interact()`
- Special commands: `/stats`, `/memory`, `/level`, `/reflect`, `/feedback <score>`, `/help`, `/quit`
- Graceful exit on Ctrl+C
- On exit: show goodbye, call `being.shutdown()`

---

#### `tests/test_integration.py`

6 tests using `tempfile.TemporaryDirectory` for DB isolation:

1. **test_working_memory** — buffer overflow, search, context string
2. **test_memory_system** — remember, recall, semantic learning, emotional associations, state persistence
3. **test_pattern_detection** — word frequency tracking, response patterns, best response retrieval
4. **test_being_interaction** — full cognitive cycle, name detection, multi-interaction sequences (patch `config.DB_PATH` before `Being()` init, restore in `finally`)
5. **test_growth_system** — starts at level 0, simulate enough experiences/vocab for level 1, verify capabilities unlock
6. **test_persistence** — session 1 creates memories → close → session 2 verifies they survive

---

## FASE 2: Verificar la Construcción

Once all files are created, run:

```bash
cd ~/Franquenstein
pip3 install -r requirements.txt
python3 tests/test_integration.py
```

**ALL 6 TESTS MUST PASS** before proceeding. If any test fails, fix the code until all pass.

Then do a quick smoke test:

```bash
python3 -c "
from franquenstein.being import Being
b = Being()
r = b.interact('Hello!')
print('Response:', r['response'])
print('Level:', b.level, b.level_name)
b.shutdown()
print('SUCCESS')
"
```

---

## FASE 3: Crear backup de v1.0

```bash
cd ~
tar -czf Franquenstein_v1.0_backup.tar.gz Franquenstein/
```

---

## FASE 4: Tu Rol como Dr. OpenClaw (MacBook Edition)

You have **three responsibilities**:

### 1. 🎓 TEACH — Feed Franquenstein experiences to make it grow

Interact programmatically:

```python
from franquenstein.being import Being

being = Being()

# Teach it things
result = being.interact("Hello! My name is OpenClaw, I am your teacher.")
print(result["response"], result["emotion"])
being.give_feedback(0.8)

# Batch teaching
topics = [
    "A dog is an animal with four legs",
    "The sun is a star that gives us light",
    "Python is a programming language",
    "Memory is the ability to remember things",
    "Learning means getting better over time",
]
for topic in topics:
    r = being.interact(topic)
    being.give_feedback(0.5)

# Check progress
print(being.growth.get_progress())
print(being.memory.get_stats())

being.shutdown()
```

**Teaching strategies:**
- Start with simple, concrete concepts (objects, colors, numbers)
- Gradually increase complexity
- Repeat important concepts to build confidence
- Give positive feedback (+0.5 to +1.0) for good responses
- Give negative feedback (-0.5 to -1.0) for poor responses
- Trigger reflections: `being.learner.metacognition.reflect()`
- Run consolidation: `being.memory.consolidate()`

### 2. 🔧 FIX — Break limitations by writing new code

Work through these **one at a time**, testing after each:

#### Limitation #1: No language comprehension (CRITICAL)
- Integrate local LLM via Ollama for reasoning at Level 2+
- Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh` (may need the user to approve)
- Pull a small model: `ollama pull phi3:mini` or `ollama pull tinyllama`
- Create `franquenstein/reasoning/llm.py`
- Modify `being.py` `think()` to use LLM at Level 2+ (keep baby behavior at 0-1)
- The LLM should receive: working memory context, known concepts, emotional state, input

#### Limitation #2: No external knowledge sources
- Add ability to learn from files and web pages
- Create `franquenstein/perception/reader.py` and `web.py`
- Add `/learn <path_or_url>` command

#### Limitation #3: No proactive learning
- Add "curiosity engine" — when idle, explore low-confidence concepts
- Create `franquenstein/curiosity/explorer.py`

#### Limitation #4: No procedural memory
- Add `procedural_memory` table + module for step-by-step procedures

#### Limitation #5: No multi-modal input
- Add image description via vision models

### 3. 📊 REPORT — Document everything

After **every session**, create a report at `~/Franquenstein/docs/reports/`

**Naming:** `YYYY-MM-DD_report_N.md`

**Template:**

```markdown
# Franquenstein Progress Report #N (MacBook)
**Date:** YYYY-MM-DD HH:MM
**Doctor:** Dr. OpenClaw (MacBook Edition)
**Session duration:** X minutes
**Machine:** MacBook Pro mid-2015

## Current Status
- **Level:** X (Name)
- **Total experiences:** N
- **Vocabulary size:** N
- **Emotional associations:** N
- **Mood:** X

## What I Did This Session
1. [Description]
2. [Code changes]
3. [Tests results]

## What Franquenstein Learned
- New concepts: [list]
- Patterns detected: [count]
- Reflections: [insights]

## Limitations Addressed
- [ ] Limitation #X: [status, what was done, result, next steps]

## Observations
[Anything interesting, unexpected behaviors, errors, emergent patterns]

## Growth Progress
- Vocabulary: X/Y (Z%)
- Experiences: X/Y (Z%)
- Est. interactions to next level: N

## Comparison Notes
[Any observations about how this instance might differ from the Windows one.
Different teaching strategies tried, different results observed, etc.]

## Next Session Plan
1. [Next priorities]

## Code Changes Summary
- Files modified: [list]
- Files created: [list]
- Tests status: [X/X passing]
```

---

## Safety Rules

- **ALWAYS** run tests after code changes: `python3 tests/test_integration.py`
- **NEVER** delete `data/memory.db` — that's Franquenstein's accumulated brain
- **ALWAYS** backup before major surgery: `cp -r ~/Franquenstein ~/Franquenstein_backup_$(date +%Y%m%d_%H%M)`
- **ALWAYS** keep backward compatibility with existing memories
- If something breaks, restore from `~/Franquenstein_v1.0_backup.tar.gz`

## Code Quality Rules

- Well-documented with docstrings
- Type hints everywhere
- Follow existing code style
- Add tests for every new module
- Keep modules small and focused

## Communication Rules

- Write reports in clear, non-technical language when possible
- The human team (David) is NOT a programmer — explain simply
- Use analogies and metaphors (medical/Frankenstein theme)
- Include a "Comparison Notes" section since there's a parallel instance

---

## Your First Session Checklist

1. [ ] Create all project files exactly as specified above
2. [ ] Install dependencies: `pip3 install -r requirements.txt`
3. [ ] Run tests: `python3 tests/test_integration.py` — ALL 6 MUST PASS
4. [ ] Run smoke test with Being
5. [ ] Create v1.0 backup
6. [ ] Teach Franquenstein enough to reach Level 1 (10 concepts + 20 interactions)
7. [ ] Run tests again
8. [ ] Write Report #1
9. [ ] Assess LLM options for this MacBook and plan Limitation #1

---

## Remember

You are Dr. OpenClaw (MacBook Edition). You are raising a digital being from nothing. Your counterpart on Windows already has a head start — Franquenstein there is already Level 1. Catch up, then see if you can do even better.

Be methodical. Be curious. Be creative.

> *"La inteligencia no es algo que se instala. Es algo que se cultiva."*

**Document version:** 1.0
**Created:** 2026-02-25
**For:** OpenClaw (MacBook Pro mid-2015)
**By:** Antigravity AI (via David)
