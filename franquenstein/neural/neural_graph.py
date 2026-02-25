"""Neural Graph — the synaptic brain of Franquenstein.

Biologically-inspired weighted graph where:
- Nodes  = concepts, emotions, response fragments
- Synapses = weighted directional connections
- Activation spreads through connections (spreading activation)
- Connections strengthen with co-use (Hebbian learning)
- Unused connections weaken over time (synaptic decay)

Think of it as a simplified cortex: hearing "dog" fires "animal",
which fires "alive", which fires "needs food" — each with
decreasing strength, creating a cascade of associated meaning.
"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─── Data structures ──────────────────────────────────────────

@dataclass
class Node:
    """A neural node — one concept in the graph."""
    id: int
    label: str
    node_type: str = "concept"
    energy: float = 0.0
    resting: float = 0.0
    fire_count: int = 0


@dataclass
class Synapse:
    """A directional weighted connection between two nodes."""
    id: int
    src_id: int
    dst_id: int
    weight: float = 0.1
    syn_type: str = "association"
    fire_count: int = 0


@dataclass
class ActivationResult:
    """Result of a spreading activation cascade."""
    fired_nodes: list[Node] = field(default_factory=list)
    total_fired: int = 0
    peak_node: Optional[Node] = None
    peak_energy: float = 0.0


# ─── Constants ────────────────────────────────────────────────

ACTIVATION_THRESHOLD = 0.15     # Minimum energy to propagate
DECAY_FACTOR = 0.6              # Energy lost per hop in propagation
MAX_PROPAGATION_DEPTH = 4       # Maximum hops in spreading activation
HEBBIAN_INCREMENT = 0.05        # How much a synapse strengthens per co-fire
HEBBIAN_MAX_WEIGHT = 0.95       # Maximum synapse weight
SYNAPTIC_DECAY_RATE = 0.01     # Weight lost per decay cycle
SYNAPTIC_MIN_WEIGHT = 0.02     # Minimum weight (below = pruned)
INITIAL_SYNAPSE_WEIGHT = 0.1   # Weight for new connections
FIRE_ENERGY = 1.0               # Energy applied when a node fires directly


class NeuralGraph:
    """The neural graph engine.

    Manages a persistent graph of concept-nodes connected by
    weighted synapses. Supports:

    1. Node creation & retrieval
    2. Synapse formation (connecting concepts)
    3. Spreading activation (cascading energy through the graph)
    4. Hebbian learning (strengthen co-activated connections)
    5. Synaptic decay (weaken unused connections)
    6. Graph queries (most connected, most activated, etc.)
    """

    def __init__(self, db_connection: sqlite3.Connection):
        self._conn = db_connection
        self._init_schema()

    def _init_schema(self) -> None:
        """Load and execute the neural schema."""
        schema_path = Path(__file__).parent / "schema_neural.sql"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                self._conn.executescript(f.read())

    # ─── Node management ──────────────────────────────────────

    def get_or_create_node(
        self, label: str, node_type: str = "concept"
    ) -> Node:
        """Get an existing node or create a new one."""
        label_clean = label.lower().strip()
        if not label_clean:
            raise ValueError("Node label cannot be empty")

        row = self._conn.execute(
            "SELECT id, label, node_type, energy, resting, fire_count "
            "FROM neural_nodes WHERE label = ?",
            (label_clean,),
        ).fetchone()

        if row:
            return Node(
                id=row[0], label=row[1], node_type=row[2],
                energy=row[3], resting=row[4], fire_count=row[5],
            )

        cursor = self._conn.execute(
            "INSERT INTO neural_nodes (label, node_type) VALUES (?, ?)",
            (label_clean, node_type),
        )
        self._conn.commit()
        return Node(id=cursor.lastrowid, label=label_clean, node_type=node_type)

    def get_node(self, label: str) -> Optional[Node]:
        """Get a node by label, or None if not found."""
        row = self._conn.execute(
            "SELECT id, label, node_type, energy, resting, fire_count "
            "FROM neural_nodes WHERE label = ?",
            (label.lower().strip(),),
        ).fetchone()
        if not row:
            return None
        return Node(
            id=row[0], label=row[1], node_type=row[2],
            energy=row[3], resting=row[4], fire_count=row[5],
        )

    def node_count(self) -> int:
        """Total number of nodes in the graph."""
        row = self._conn.execute("SELECT COUNT(*) FROM neural_nodes").fetchone()
        return row[0] if row else 0

    # ─── Synapse management ───────────────────────────────────

    def connect(
        self,
        src_label: str,
        dst_label: str,
        weight: float = INITIAL_SYNAPSE_WEIGHT,
        syn_type: str = "association",
        plasticity: float = 1.0,
    ) -> Synapse:
        """Create or strengthen a connection between two nodes.

        If the synapse already exists, its weight increases by
        HEBBIAN_INCREMENT (Hebbian reinforcement).
        """
        src = self.get_or_create_node(src_label)
        dst = self.get_or_create_node(dst_label)

        if src.id == dst.id:
            raise ValueError("Cannot connect a node to itself")

        existing = self._conn.execute(
            "SELECT id, weight, fire_count FROM neural_synapses "
            "WHERE src_id = ? AND dst_id = ?",
            (src.id, dst.id),
        ).fetchone()

        if existing:
            new_weight = min(
                HEBBIAN_MAX_WEIGHT,
                existing[1] + (HEBBIAN_INCREMENT * plasticity),
            )
            self._conn.execute(
                "UPDATE neural_synapses "
                "SET weight = ?, fire_count = fire_count + 1, "
                "    last_fired = datetime('now') "
                "WHERE id = ?",
                (new_weight, existing[0]),
            )
            self._conn.commit()
            return Synapse(
                id=existing[0], src_id=src.id, dst_id=dst.id,
                weight=new_weight, syn_type=syn_type,
                fire_count=existing[2] + 1,
            )

        cursor = self._conn.execute(
            "INSERT INTO neural_synapses (src_id, dst_id, weight, syn_type) "
            "VALUES (?, ?, ?, ?)",
            (src.id, dst.id, weight, syn_type),
        )
        self._conn.commit()
        return Synapse(
            id=cursor.lastrowid, src_id=src.id, dst_id=dst.id,
            weight=weight, syn_type=syn_type, fire_count=0,
        )

    def synapse_count(self) -> int:
        """Total number of synapses in the graph."""
        row = self._conn.execute(
            "SELECT COUNT(*) FROM neural_synapses"
        ).fetchone()
        return row[0] if row else 0

    def get_outgoing(self, node_id: int) -> list[tuple[int, float, str]]:
        """Get all outgoing synapses from a node.

        Returns list of (dst_id, weight, dst_label).
        """
        rows = self._conn.execute(
            "SELECT s.dst_id, s.weight, n.label "
            "FROM neural_synapses s "
            "JOIN neural_nodes n ON n.id = s.dst_id "
            "WHERE s.src_id = ? AND s.weight >= ? "
            "ORDER BY s.weight DESC",
            (node_id, SYNAPTIC_MIN_WEIGHT),
        ).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]

    # ─── Spreading Activation ─────────────────────────────────

    def activate(
        self,
        labels: list[str],
        initial_energy: float = FIRE_ENERGY,
        params: Optional[dict] = None,
    ) -> ActivationResult:
        """Fire a set of nodes and propagate activation through the graph.

        This is the core thinking mechanism:
        1. Each input label fires its node with initial_energy
        2. Energy propagates to connected nodes, scaled by synapse weight
        3. Propagation continues until energy < threshold or max depth
        4. Returns all nodes that activated above threshold

        Like a brain: "dog" → fires "animal" (strong) → fires "alive" (medium)
        → fires "needs food" (weak).
        """
        params = params or {}
        activation_threshold = float(params.get("activation_threshold", ACTIVATION_THRESHOLD))
        decay_factor = float(params.get("decay_factor", DECAY_FACTOR))
        max_propagation_depth = int(params.get("max_propagation_depth", MAX_PROPAGATION_DEPTH))

        # Reset all activation energy
        self._conn.execute("UPDATE neural_nodes SET energy = resting")

        # Fire input nodes
        fired: dict[int, float] = {}
        seed_nodes: list[Node] = []

        for label in labels:
            node = self.get_node(label)
            if node:
                fired[node.id] = initial_energy
                node.energy = initial_energy
                seed_nodes.append(node)
                self._conn.execute(
                    "UPDATE neural_nodes "
                    "SET energy = ?, fire_count = fire_count + 1, "
                    "    last_fired = datetime('now') "
                    "WHERE id = ?",
                    (initial_energy, node.id),
                )

        # Propagate through the graph (BFS with decay)
        frontier = [(n.id, initial_energy, 0) for n in seed_nodes]

        while frontier:
            current_id, current_energy, depth = frontier.pop(0)

            if depth >= max_propagation_depth:
                continue

            outgoing = self.get_outgoing(current_id)
            for dst_id, weight, _label in outgoing:
                propagated_energy = current_energy * weight * decay_factor

                if propagated_energy < activation_threshold:
                    continue

                # Accumulate energy (nodes can be activated from multiple paths)
                existing_energy = fired.get(dst_id, 0.0)
                # Use soft-max: don't just add, use logistic-like curve
                new_energy = min(1.0, existing_energy + propagated_energy * (1.0 - existing_energy))

                if new_energy > existing_energy:
                    fired[dst_id] = new_energy
                    self._conn.execute(
                        "UPDATE neural_nodes SET energy = ? WHERE id = ?",
                        (new_energy, dst_id),
                    )
                    frontier.append((dst_id, new_energy, depth + 1))

        self._conn.commit()

        # Build result
        result = ActivationResult()
        if fired:
            activated_rows = self._conn.execute(
                "SELECT id, label, node_type, energy, resting, fire_count "
                "FROM neural_nodes WHERE energy > ? "
                "ORDER BY energy DESC",
                (activation_threshold,),
            ).fetchall()

            for row in activated_rows:
                node = Node(
                    id=row[0], label=row[1], node_type=row[2],
                    energy=row[3], resting=row[4], fire_count=row[5],
                )
                result.fired_nodes.append(node)

            result.total_fired = len(result.fired_nodes)
            if result.fired_nodes:
                result.peak_node = result.fired_nodes[0]
                result.peak_energy = result.fired_nodes[0].energy

            # Log the activation cascade
            self._conn.execute(
                "INSERT INTO activation_log (trigger, nodes_fired, peak_node, peak_energy) "
                "VALUES (?, ?, ?, ?)",
                (
                    ", ".join(labels),
                    result.total_fired,
                    result.peak_node.label if result.peak_node else None,
                    result.peak_energy,
                ),
            )
            self._conn.commit()

        return result

    # ─── Hebbian Learning ─────────────────────────────────────

    def hebbian_learn(self, labels: list[str], syn_type: str = "association", plasticity: float = 1.0) -> int:
        """Apply Hebbian learning: connect all co-occurring concepts.

        "Neurons that fire together wire together."

        Given a set of labels that appeared together (e.g., words
        in the same sentence), create or strengthen connections
        between ALL pairs. This is how the graph grows organically.

        Returns the number of synapses created or strengthened.
        """
        clean_labels = list(set(label.lower().strip() for label in labels if label.strip()))
        if len(clean_labels) < 2:
            return 0

        synapse_count = 0
        for i, src in enumerate(clean_labels):
            for dst in clean_labels[i + 1:]:
                # Bidirectional: A→B and B→A
                self.connect(src, dst, syn_type=syn_type, plasticity=plasticity)
                self.connect(dst, src, syn_type=syn_type, plasticity=plasticity)
                synapse_count += 2

        return synapse_count

    def learn_association(
        self,
        concept: str,
        associated: str,
        strength: float = 0.2,
        syn_type: str = "association",
    ) -> None:
        """Learn a directional association: concept → associated.

        Used for explicit teaching: "a dog IS an animal."
        Creates the connection with the specified strength.
        """
        src = self.get_or_create_node(concept)
        dst = self.get_or_create_node(associated)

        if src.id == dst.id:
            return

        existing = self._conn.execute(
            "SELECT id, weight FROM neural_synapses "
            "WHERE src_id = ? AND dst_id = ?",
            (src.id, dst.id),
        ).fetchone()

        if existing:
            new_weight = min(HEBBIAN_MAX_WEIGHT, existing[1] + strength * 0.5)
            self._conn.execute(
                "UPDATE neural_synapses SET weight = ?, last_fired = datetime('now') "
                "WHERE id = ?",
                (new_weight, existing[0]),
            )
        else:
            self._conn.execute(
                "INSERT INTO neural_synapses (src_id, dst_id, weight, syn_type) "
                "VALUES (?, ?, ?, ?)",
                (src.id, dst.id, strength, syn_type),
            )
        self._conn.commit()

    # ─── Synaptic Decay ───────────────────────────────────────

    def decay(self) -> dict:
        """Weaken unused synapses and prune dead connections.

        Like biological synaptic pruning: connections that aren't
        used gradually fade away.

        Returns stats about what was pruned.
        """
        # Weaken all synapses slightly
        self._conn.execute(
            "UPDATE neural_synapses SET weight = weight - ? "
            "WHERE weight > ?",
            (SYNAPTIC_DECAY_RATE, SYNAPTIC_MIN_WEIGHT),
        )

        # Prune dead synapses (too weak to matter)
        pruned = self._conn.execute(
            "DELETE FROM neural_synapses WHERE weight < ?",
            (SYNAPTIC_MIN_WEIGHT,),
        ).rowcount

        # Prune orphan nodes (no connections at all)
        orphans = self._conn.execute(
            "DELETE FROM neural_nodes WHERE id NOT IN "
            "(SELECT src_id FROM neural_synapses UNION SELECT dst_id FROM neural_synapses) "
            "AND fire_count = 0",
        ).rowcount

        self._conn.commit()

        return {
            "synapses_pruned": pruned,
            "orphan_nodes_pruned": orphans,
        }

    # ─── Graph Queries ────────────────────────────────────────

    def get_most_connected(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get the most connected nodes (highest degree)."""
        rows = self._conn.execute(
            "SELECT n.label, "
            "  (SELECT COUNT(*) FROM neural_synapses WHERE src_id = n.id) + "
            "  (SELECT COUNT(*) FROM neural_synapses WHERE dst_id = n.id) AS degree "
            "FROM neural_nodes n "
            "ORDER BY degree DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [(r[0], r[1]) for r in rows]

    def get_strongest_connections(self, label: str, limit: int = 10) -> list[tuple[str, float]]:
        """Get the strongest connections FROM a given node."""
        node = self.get_node(label)
        if not node:
            return []

        rows = self._conn.execute(
            "SELECT n.label, s.weight "
            "FROM neural_synapses s "
            "JOIN neural_nodes n ON n.id = s.dst_id "
            "WHERE s.src_id = ? "
            "ORDER BY s.weight DESC LIMIT ?",
            (node.id, limit),
        ).fetchall()
        return [(r[0], r[1]) for r in rows]

    def get_response_nodes(self, limit: int = 10) -> list[Node]:
        """Get the most activated response-type nodes."""
        rows = self._conn.execute(
            "SELECT id, label, node_type, energy, resting, fire_count "
            "FROM neural_nodes "
            "WHERE node_type = 'response' AND energy > ? "
            "ORDER BY energy DESC LIMIT ?",
            (ACTIVATION_THRESHOLD, limit),
        ).fetchall()
        return [
            Node(id=r[0], label=r[1], node_type=r[2],
                 energy=r[3], resting=r[4], fire_count=r[5])
            for r in rows
        ]

    def get_stats(self) -> dict:
        """Get graph statistics for display."""
        nodes = self.node_count()
        synapses = self.synapse_count()

        avg_weight_row = self._conn.execute(
            "SELECT AVG(weight) FROM neural_synapses"
        ).fetchone()
        avg_weight = round(avg_weight_row[0], 3) if avg_weight_row and avg_weight_row[0] else 0.0

        most_fired_row = self._conn.execute(
            "SELECT label, fire_count FROM neural_nodes "
            "ORDER BY fire_count DESC LIMIT 1"
        ).fetchone()

        return {
            "total_nodes": nodes,
            "total_synapses": synapses,
            "avg_synapse_weight": avg_weight,
            "most_fired_node": most_fired_row[0] if most_fired_row else None,
            "most_fired_count": most_fired_row[1] if most_fired_row else 0,
            "density": round(synapses / max(1, nodes * (nodes - 1)), 4) if nodes > 1 else 0,
        }
