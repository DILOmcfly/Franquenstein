-- ═══════════════════════════════════════════════════════════
-- Franquenstein — Esquema de Memoria Persistente
-- ═══════════════════════════════════════════════════════════

-- Memoria Episódica: experiencias completas con contexto
CREATE TABLE IF NOT EXISTS episodic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    input_text TEXT NOT NULL,
    output_text TEXT,
    context TEXT,                    -- JSON con contexto adicional
    emotion TEXT DEFAULT 'neutral',  -- curiosidad, confusión, satisfacción, etc.
    emotion_intensity REAL DEFAULT 0.5,  -- 0.0 a 1.0
    feedback_score REAL DEFAULT 0.0,     -- -1.0 (malo) a 1.0 (bueno)
    access_count INTEGER DEFAULT 0,
    last_accessed TEXT,
    importance REAL DEFAULT 0.5     -- 0.0 a 1.0, para decay/consolidation
);

-- Memoria Semántica: hechos y conceptos aprendidos
CREATE TABLE IF NOT EXISTS semantic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept TEXT NOT NULL UNIQUE,
    definition TEXT,
    associations TEXT,              -- JSON: lista de conceptos relacionados
    confidence REAL DEFAULT 0.1,    -- 0.0 a 1.0, crece con repetición
    source_count INTEGER DEFAULT 1, -- Cuántas experiencias lo originaron
    first_learned TEXT NOT NULL DEFAULT (datetime('now')),
    last_reinforced TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Memoria Emocional: asociaciones sentimentales a conceptos
CREATE TABLE IF NOT EXISTS emotional_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept TEXT NOT NULL,
    emotion TEXT NOT NULL,           -- curiosidad, alegría, confusión, frustración
    intensity REAL DEFAULT 0.5,      -- 0.0 a 1.0
    occurrence_count INTEGER DEFAULT 1,
    last_felt TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(concept, emotion)
);

-- Patrones detectados: para el motor de aprendizaje
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,       -- 'word_freq', 'bigram', 'response_pattern'
    pattern_key TEXT NOT NULL,
    pattern_value TEXT,               -- JSON con datos del patrón
    frequency INTEGER DEFAULT 1,
    confidence REAL DEFAULT 0.1,
    first_seen TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(pattern_type, pattern_key)
);

-- Estado del ser digital: nivel, métricas, etc.
CREATE TABLE IF NOT EXISTS being_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memory(timestamp);
CREATE INDEX IF NOT EXISTS idx_episodic_emotion ON episodic_memory(emotion);
CREATE INDEX IF NOT EXISTS idx_episodic_importance ON episodic_memory(importance);
CREATE INDEX IF NOT EXISTS idx_semantic_concept ON semantic_memory(concept);
CREATE INDEX IF NOT EXISTS idx_semantic_confidence ON semantic_memory(confidence);
CREATE INDEX IF NOT EXISTS idx_emotional_concept ON emotional_memory(concept);
CREATE INDEX IF NOT EXISTS idx_patterns_type_key ON patterns(pattern_type, pattern_key);
