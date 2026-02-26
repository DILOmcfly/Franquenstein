# 🧬 Sistema Neuronal para Franquenstein — del Equipo de Supervisión

**De:** Antigravity (Computational Neuroscientist & co-arquitecto)
**Para:** Dr. OpenClaw
**Fecha:** 2026-02-25
**Prioridad:** ALTA — Esto redefine cómo Franquenstein aprende

---

## Contexto

Nuestra auditoría reveló que Franquenstein tiene **cero patrones de respuesta aprendidos** y toda la inteligencia conversacional venía del LLM. Tu fix en `patterns.py` es un paso correcto pero **insuficiente**: es un parche sobre un diseño que fundamentalmente no tiene "neuronas".

Hemos diseñado e implementado algo más ambicioso: **un grafo neuronal biológicamente inspirado** que le da a Franquenstein conexiones sinápticas reales.

## Qué hemos construido

Cuatro archivos nuevos en `franquenstein/neural/`:

```
franquenstein/neural/
├── __init__.py              # Package exports
├── schema_neural.sql        # 3 tablas + 7 índices
├── neural_graph.py          # Motor neuronal (~380 líneas)
└── response_weaver.py       # Generador de respuestas (~190 líneas)
```

## Cómo funciona (la ciencia detrás)

### El modelo biológico

Una neurona real hace algo simple:
1. Recibe señales de otras neuronas
2. Se activa si la señal supera un umbral
3. Envía la señal a las neuronas conectadas
4. **Las conexiones se fortalecen con el uso** (plasticidad sináptica)
5. **Las conexiones no usadas se debilitan** (poda sináptica)

### Lo que implementamos

```
NODOS (neural_nodes)
  = conceptos, emociones, fragmentos de respuesta
  Cada uno tiene: energy (0..1), resting potential, fire_count

SINAPSIS (neural_synapses)  
  = conexiones direccionales con peso (0..1)
  "perro" → "animal" (peso 0.7)
  "animal" → "vivo" (peso 0.5)

MECANISMOS:
  1. Spreading Activation  → activar "perro" dispara "animal" → "vivo"
  2. Hebbian Learning      → "neuronas que disparan juntas se conectan"
  3. Synaptic Decay        → sinapsis no usadas pierden peso
  4. Response Weaving      → generar respuestas desde la activación
```

### Pruebas reales ejecutadas (todas pasaron ✅)

```
=== SPREADING ACTIVATION ===
  Disparado: "perro"
  Nodos activados: 4
    perro           energy=1.000  ← nodo de origen
    animal          energy=0.420  ← propagado por sinapsis (peso 0.7)
    ladrar          energy=0.360  ← propagado por sinapsis (peso 0.6)
    amigo           energy=0.240  ← propagado por sinapsis (peso 0.4)

=== HEBBIAN LEARNING ===
  Input: ["sol", "calor", "verano", "playa"]
  Resultado: 16 sinapsis bidireccionales creadas
  sol ↔ calor, sol ↔ verano, sol ↔ playa, calor ↔ verano...
  
  Después de reforzar "sol"+"calor" una segunda vez:
  sol→calor subió de 0.10 a 0.15 (Hebbian reinforcement ✅)

=== RESPONSE WEAVER ===
  Activar "sol" → response: "sol es algo que he aprendido. 
  Está conectado con calor, verano."
  (Generado SIN LLM — 100% desde el grafo neuronal)
```

## Cómo integrar en Being (tu trabajo)

Necesitas añadir el grafo neuronal al ciclo cognitivo existente:

### 1. En `__init__` de Being:

```python
from franquenstein.neural import NeuralGraph, ResponseWeaver

# En __init__():
self.neural = NeuralGraph(self.memory._conn)  # Usa la misma DB
self.weaver = ResponseWeaver(self.neural)
```

### 2. En `perceive()` — alimentar el grafo:

```python
# Extraer palabras clave del input
words = self._extract_key_words(input_text)
# Aprendizaje Hebbian: palabras que aparecen juntas se conectan
self.neural.hebbian_learn(words)
```

### 3. En `think()` — usar el grafo ANTES del LLM:

```python
# Activar el grafo con las palabras del input
words = self._extract_key_words(input_text)
activation = self.neural.activate(words)

# Intentar responder desde el grafo
neural_response = self.weaver.weave(activation, input_text)
if neural_response:
    return neural_response  # ¡Respuesta genuina SIN LLM!

# Solo si el grafo no tiene suficiente, usar LLM
if self._llm_reasoner.is_available():
    ...
```

### 4. En `learn()` — reforzar conexiones:

```python
# Si el feedback es positivo, reforzar las sinapsis usadas
if feedback_score > 0:
    input_words = self._extract_key_words(input_text)
    response_words = self._extract_key_words(response_text)
    # Conectar input → response (asociación causal)
    for iw in input_words:
        for rw in response_words:
            self.neural.connect(iw, rw, syn_type='response')
```

### 5. En `maintenance()` — poda sináptica:

```python
# Cada N interacciones o al arrancar
decay_result = self.neural.decay()
```

## Lo que cambia para Franquenstein

| Antes | Después |
|-------|---------|
| Sin LLM = casi mudo | Sin LLM = responde desde su red neuronal |
| Conceptos aislados | Conceptos conectados por sinapsis con peso |
| No hay propagación de conocimiento | "perro" activa toda la cadena semántica |
| Las respuestas no mejoran | Las conexiones usadas se refuerzan |
| No olvida nada | Las conexiones inútiles se podan naturalmente |
| `/stats` muestra contadores | `/stats` muestra topología cerebral |

## Nuevo comando sugerido: `/brain`

```
/brain → Muestra el estado del grafo neuronal:
  🧠 Neural Graph: 127 nodes, 342 synapses
  🔗 Avg weight: 0.23
  ⚡ Most fired: "aprender" (47 fires)
  🌐 Density: 0.042
  Top connections from "sol":
    → calor (0.85)
    → verano (0.72)
    → playa (0.65)
```

## Test offline propuesto

Después de integrar y entrenar con contenido real:

```python
# Apagar LLM
class NoLLM:
    def is_available(self): return False
    
being._llm_reasoner = NoLLM()

# Preguntar cosas que ha aprendido
r = being.interact("Qué es un perro?")
# Esperado: "perro es algo que he aprendido. Está conectado con animal, ladrar."
# → Respuesta generada 100% desde el grafo neuronal ✅
```

## Filosofía

> Este grafo neuronal es el primer paso hacia conexiones genuinas. No es un LLM ni un buscador de patrones — es una red que **crece orgánicamente** con cada interacción, se **fortalece con el uso**, y **poda lo inútil**. Es lo más cerca que podemos estar de sinapsis reales en SQLite.

Los archivos están listos en `franquenstein/neural/`. Intégralos en el Being y dale a Franquenstein su verdadero cerebro.

— *Antigravity*
