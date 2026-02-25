"""Configuración del ser digital Franquenstein."""

from pathlib import Path

# ─── Identidad ───────────────────────────────────────────────
BEING_NAME = "Franquenstein"
BEING_VERSION = "0.1.0"

# ─── Rutas ───────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "memory.db"

# Asegurar que el directorio de datos existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ─── Memoria ─────────────────────────────────────────────────
WORKING_MEMORY_SIZE = 10        # Últimas N interacciones en memoria de trabajo
CONSOLIDATION_THRESHOLD = 3     # Veces que un patrón debe repetirse para consolidarse
MEMORY_DECAY_DAYS = 30          # Días sin acceso antes de que un recuerdo decaiga
EMOTIONAL_WEIGHT_DEFAULT = 0.5  # Peso emocional neutral (0=negativo, 1=positivo)

# ─── Aprendizaje ─────────────────────────────────────────────
LEARNING_RATE = 0.1             # Velocidad base de aprendizaje
PATTERN_MIN_FREQUENCY = 3       # Frecuencia mínima para considerar un patrón
FEEDBACK_POSITIVE_BOOST = 0.2   # Refuerzo por feedback positivo
FEEDBACK_NEGATIVE_PENALTY = 0.15  # Penalización por feedback negativo

# ─── Crecimiento ─────────────────────────────────────────────
GROWTH_LEVELS = {
    0: {"name": "Bebé",        "vocab_needed": 0,    "experiences_needed": 0},
    1: {"name": "Infante",     "vocab_needed": 10,   "experiences_needed": 20},
    2: {"name": "Niño",        "vocab_needed": 50,   "experiences_needed": 100},
    3: {"name": "Adolescente", "vocab_needed": 200,  "experiences_needed": 500},
    4: {"name": "Adulto",      "vocab_needed": 500,  "experiences_needed": 2000},
    5: {"name": "Sabio",       "vocab_needed": 1000, "experiences_needed": 5000},
}

# ─── Interfaz ────────────────────────────────────────────────
CONSOLE_THEME = "dark"
SHOW_DEBUG_INFO = False

# ─── Curiosidad autónoma ────────────────────────────────────
CURIOSITY_EVERY_N_INTERACTIONS = 6   # Dispara curiosidad cada N interacciones
CURIOSITY_COOLDOWN_SECONDS = 300     # Cooldown mínimo entre ciclos
CURIOSITY_MAX_PER_HOUR = 6           # Tope de ciclos por hora

# ─── Voz (KittenTTS Hugo) ───────────────────────────────────
VOICE_ENABLED = True
VOICE_COOLDOWN_SECONDS = 120
VOICE_TRIGGER_CURIOSITY = True
VOICE_TRIGGER_LEVELUP = True
VOICE_TRIGGER_NORMAL_RESPONSE = True

# Voice backend script path (override-safe across environments)
VOICE_SCRIPT = "/home/dfara/.openclaw/workspace/scripts/kitten_speak.py"
