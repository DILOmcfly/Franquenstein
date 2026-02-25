"""Response Weaver — generates responses from neural graph activation.

Instead of asking an LLM "what should I say?", this module looks at
which concepts are most activated after spreading activation and
weaves a response from the neural graph itself.

The hierarchy:
1. If a response-type node is strongly activated → use it directly
2. If concept nodes are activated → compose a response from them
3. If nothing is activated → fall through to LLM or fallback
"""

from __future__ import annotations

import random
from typing import Optional

from franquenstein.neural.neural_graph import ActivationResult, Node


# ─── Response templates ──────────────────────────────────────

_TEMPLATES = {
    "association": [
        "Cuando pienso en {a}, me viene a la mente {b}.",
        "{a} me recuerda a {b}.",
        "Creo que {a} está conectado con {b}.",
        "Sé que {a} tiene que ver con {b}.",
    ],
    "explanation": [
        "{concept} es algo que he aprendido. {detail}",
        "Sobre {concept}: {detail}",
        "{concept}... {detail}",
    ],
    "uncertainty": [
        "{concept} me suena, pero aún no lo tengo claro.",
        "Sé un poco sobre {concept}, pero necesito aprender más.",
        "He oído sobre {concept}, ¿me puedes contar más?",
    ],
    "curiosity": [
        "¿{concept} se conecta con {related}? Me gustaría explorar eso.",
        "Me pregunto cómo se relacionan {concept} y {related}.",
    ],
    "greeting": [
        "¡Hola! Tengo {nodes} ideas conectadas por {synapses} caminos neuronales.",
        "¡Hey! Mi cerebro tiene {nodes} conceptos con {synapses} conexiones.",
    ],
    "identity": [
        "Soy Franquenstein. Tengo {nodes} conceptos en mi red neuronal y cada día hago más conexiones.",
        "Me llamo Franquenstein. Mi cerebro tiene {synapses} conexiones sinápticas entre {nodes} ideas.",
    ],
    "reflection": [
        "Lo que más sé es sobre {top}. Lo he pensado {count} veces.",
        "Mi neurona más activa es '{top}' — la he usado {count} veces.",
    ],
}


class ResponseWeaver:
    """Weave responses from neural graph activation patterns.

    This is Franquenstein's own voice — not the LLM's, not a template,
    but genuine expression based on which neural pathways are active.
    """

    def __init__(self, neural_graph):
        self.graph = neural_graph

    def weave(
        self,
        activation: ActivationResult,
        input_text: str = "",
        graph_stats: Optional[dict] = None,
        tone: str = "neutral",
    ) -> Optional[str]:
        """Generate a response from the current neural activation state.

        Returns None if the activation is too weak to form a meaningful
        response (in which case the caller should fall back to LLM).
        """
        if not activation.fired_nodes:
            return None

        input_lower = input_text.lower().strip()

        # ── Priority 1: Dedicated response nodes ──
        response_nodes = [
            n for n in activation.fired_nodes
            if n.node_type == "response" and n.energy > 0.3
        ]
        if response_nodes:
            return response_nodes[0].label

        # ── Priority 2: Handle common patterns ──
        if self._is_greeting(input_lower):
            return self._greeting_response(graph_stats)

        if self._is_identity_question(input_lower):
            return self._identity_response(graph_stats)

        if self._is_reflection_request(input_lower):
            return self._reflection_response()

        # ── Priority 3: Compose from activated concepts ──
        concept_nodes = [
            n for n in activation.fired_nodes
            if n.node_type == "concept" and n.energy > 0.2
        ]

        response = None
        if len(concept_nodes) >= 2:
            response = self._association_response(concept_nodes)
        elif len(concept_nodes) == 1:
            response = self._single_concept_response(concept_nodes[0])

        # ── Priority 4: Not enough activation ──
        if not response:
            return None

        if tone == "warm":
            return random.choice([
                f"Me gusta esta conexión: {response}",
                f"Suena bien así: {response}",
            ])
        if tone == "focused":
            return random.choice([
                f"Punto clave: {response}",
                f"En concreto: {response}",
            ])
        if tone == "defensive":
            return random.choice([
                f"Con cautela: {response}",
                f"Voy paso a paso: {response}",
            ])
        if tone == "reflective":
            return random.choice([
                f"Si lo miro con calma: {response}",
                f"Pensándolo bien: {response}",
            ])
        return response

    # ─── Response generators ──────────────────────────────────

    def _greeting_response(self, stats: Optional[dict]) -> str:
        stats = stats or self.graph.get_stats()
        template = random.choice(_TEMPLATES["greeting"])
        return template.format(
            nodes=stats.get("total_nodes", 0),
            synapses=stats.get("total_synapses", 0),
        )

    def _identity_response(self, stats: Optional[dict]) -> str:
        stats = stats or self.graph.get_stats()
        template = random.choice(_TEMPLATES["identity"])
        return template.format(
            nodes=stats.get("total_nodes", 0),
            synapses=stats.get("total_synapses", 0),
        )

    def _reflection_response(self) -> str:
        stats = self.graph.get_stats()
        top = stats.get("most_fired_node", "algo")
        count = stats.get("most_fired_count", 0)
        template = random.choice(_TEMPLATES["reflection"])
        return template.format(top=top, count=count)

    def _association_response(self, nodes: list[Node]) -> str:
        """Compose a response from multiple activated concepts."""
        # Take the two strongest
        a = nodes[0]
        b = nodes[1]

        # Check if there's a meaningful connection between them
        connections = self.graph.get_strongest_connections(a.label, limit=5)
        connection_labels = [c[0] for c in connections]

        if b.label in connection_labels:
            template = random.choice(_TEMPLATES["association"])
            return template.format(a=a.label, b=b.label)

        # They're both active but not directly connected — curiosity!
        template = random.choice(_TEMPLATES["curiosity"])
        return template.format(concept=a.label, related=b.label)

    def _single_concept_response(self, node: Node) -> str:
        """Respond about a single activated concept."""
        connections = self.graph.get_strongest_connections(node.label, limit=3)

        if connections:
            detail_parts = [c[0] for c in connections[:2]]
            detail = f"Está conectado con {', '.join(detail_parts)}."
            template = random.choice(_TEMPLATES["explanation"])
            return template.format(concept=node.label, detail=detail)

        template = random.choice(_TEMPLATES["uncertainty"])
        return template.format(concept=node.label)

    # ─── Input classifiers ────────────────────────────────────

    @staticmethod
    def _is_greeting(text: str) -> bool:
        greetings = {"hola", "hello", "hey", "hi", "buenas", "buenos días",
                     "buenas tardes", "buenas noches", "qué tal", "como estas",
                     "que tal", "saludos"}
        words = set(text.replace("!", "").replace("¿", "").replace("?", "").split())
        return bool(words & greetings)

    @staticmethod
    def _is_identity_question(text: str) -> bool:
        markers = ["quien eres", "quién eres", "como te llamas", "cómo te llamas",
                    "tu nombre", "what is your name", "who are you"]
        return any(m in text for m in markers)

    @staticmethod
    def _is_reflection_request(text: str) -> bool:
        markers = ["que sabes", "qué sabes", "que has aprendido", "qué has aprendido",
                    "reflecciona", "reflexiona", "piensa en ti"]
        return any(m in text for m in markers)
