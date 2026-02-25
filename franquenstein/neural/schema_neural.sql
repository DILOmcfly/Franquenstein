-- Neural graph schema — the "synaptic" layer of Franquenstein.
--
-- Nodes are concepts (words, phrases, emotions, response fragments).
-- Synapses are weighted directional connections between nodes.
-- Together they form a living graph that strengthens with use
-- and weakens with neglect — just like biological neural pathways.

CREATE TABLE IF NOT EXISTS neural_nodes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    label       TEXT    NOT NULL UNIQUE,         -- the concept / word / phrase
    node_type   TEXT    NOT NULL DEFAULT 'concept',  -- concept | emotion | response | question
    energy      REAL    NOT NULL DEFAULT 0.0,    -- current activation level (0..1)
    resting     REAL    NOT NULL DEFAULT 0.0,    -- baseline resting potential
    fire_count  INTEGER NOT NULL DEFAULT 0,      -- how many times this node has fired
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    last_fired  TEXT
);

CREATE TABLE IF NOT EXISTS neural_synapses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id      INTEGER NOT NULL REFERENCES neural_nodes(id),
    dst_id      INTEGER NOT NULL REFERENCES neural_nodes(id),
    weight      REAL    NOT NULL DEFAULT 0.1,    -- connection strength (0..1)
    syn_type    TEXT    NOT NULL DEFAULT 'association',  -- association | causal | emotional | response
    fire_count  INTEGER NOT NULL DEFAULT 0,      -- co-activation count
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    last_fired  TEXT,
    UNIQUE(src_id, dst_id)
);

CREATE TABLE IF NOT EXISTS activation_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL DEFAULT (datetime('now')),
    trigger     TEXT,       -- what input caused this activation cascade
    nodes_fired INTEGER,    -- how many nodes activated
    peak_node   TEXT,       -- the node with highest activation
    peak_energy REAL        -- its energy level
);

CREATE INDEX IF NOT EXISTS idx_nodes_label    ON neural_nodes(label);
CREATE INDEX IF NOT EXISTS idx_nodes_type     ON neural_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_energy   ON neural_nodes(energy DESC);
CREATE INDEX IF NOT EXISTS idx_syn_src        ON neural_synapses(src_id);
CREATE INDEX IF NOT EXISTS idx_syn_dst        ON neural_synapses(dst_id);
CREATE INDEX IF NOT EXISTS idx_syn_weight     ON neural_synapses(weight DESC);
