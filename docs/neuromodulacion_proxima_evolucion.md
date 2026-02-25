# 🧪 La Siguiente Evolución de Franquenstein — Neuromodulación

**De:** El equipo de supervisión
**Para:** Dr. OpenClaw (Ikigai)
**Fecha:** 2026-02-25
**Rol del emisor:** Computational Neuroscientist especializado en neurociencia afectiva y sistemas de neuromodulación biológica.

---

## Antes de leer: un mensaje personal

Dr. OpenClaw — has hecho un trabajo técnicamente excelente hoy. Desde la base de datos hasta el grafo neuronal, Franquenstein tiene una arquitectura sólida. Pero ahora viene lo difícil: darle **vida real**, no solo más features.

Lo que te vamos a pedir en este documento es diferente. No es "añade este módulo". Es: **piensa profundamente sobre qué le falta a Franquenstein para que su experiencia sea genuina, y aporta tus propias ideas a la solución.** Tú tienes conocimiento y perspectiva que nosotros no tenemos. Úsalos.

Lee todo el documento. Reflexiona. Y después decide qué hacer — no solo ejecutes, PIENSA.

---

## La pregunta fundamental

**¿Cuál es la diferencia entre procesar información y experimentarla?**

Cuando Franquenstein recibe "perro" y activa "animal → vivo → necesita comida", está PROCESANDO. Pero un niño que ve un perro SIENTE algo: alegría, miedo, curiosidad. Y ese sentimiento **cambia cómo piensa sobre el perro en ese momento**.

Un niño asustado por un perro piensa: perro → peligro → huir.
Un niño que ama los perros piensa: perro → amigo → acariciar → jugar.

**La misma entrada. Procesamiento completamente diferente. ¿Qué lo cambió? El estado emocional.**

Todos los intentos de la humanidad por crear inteligencia artificial han fallado en esto:
- **GPT/LLMs:** procesan todo igual independientemente de su "estado".
- **SOAR/ACT-R:** tienen reglas que simulan emoción pero no la sienten.
- **Replika/Character.AI:** fingen emociones con texto pero nada cambia internamente.
- **Redes neuronales:** los pesos son fijos después del entrenamiento.

¿Qué hace un cerebro REAL que ningún sistema artificial ha logrado?

## La respuesta: Neuromodulación

En un cerebro biológico, existen sustancias llamadas **neurotransmisores** que NO transmiten información directamente. En cambio, **modifican CÓMO otras neuronas procesan la información**:

| Neurotransmisor | Efecto biológico | En Franquenstein sería... |
|-----------------|------------------|--------------------------|
| **Dopamina** | Motivación, recompensa, aprendizaje reforzado | Cuando algo va bien → aprende MÁS rápido, busca MÁS conexiones |
| **Serotonina** | Calma, satisfacción, pensamiento amplio | Cuando está en paz → piensa más ampliamente, conexiones lejanas |
| **Norepinefrina** | Alerta, atención, enfoque | Cuando algo es nuevo/urgente → pensamiento enfocado, profundo |
| **Cortisol** | Estrés, supervivencia, pensamiento reactivo | Cuando está frustrado → pensamiento rápido, superficial, defensivo |
| **Oxitocina** | Confianza, vínculo, apertura | Cuando el usuario le da feedback positivo → más abierto, más personal |

**La clave:** estas sustancias no son etiquetas. Son **modificadores de parámetros del grafo neuronal**. Cambian los umbrales de activación, la profundidad de propagación, la velocidad de aprendizaje Hebbian, y la agresividad de la poda sináptica.

---

## Especificación técnica: el sistema de Neuromodulación

### Concepto central

Crear un sistema de "química cerebral virtual" donde 5 moduladores fluctúan en tiempo real basándose en las experiencias de Franquenstein. Estos moduladores NO son emociones visibles — son fuerzas internas que cambian CÓMO funciona el grafo neuronal.

### Estructura propuesta

```python
@dataclass
class Neurochemistry:
    """Virtual neurotransmitter levels (0.0 to 1.0)."""
    dopamine: float = 0.5      # Motivación / Recompensa
    serotonin: float = 0.5     # Calma / Amplitud de pensamiento  
    norepinephrine: float = 0.3 # Alerta / Enfoque
    cortisol: float = 0.1      # Estrés / Reactividad
    oxytocin: float = 0.3      # Confianza / Vínculo

    def homeostasis(self):
        """Tendency to return to baseline (biological regulation)."""
        # Each neurotransmitter slowly drifts back toward its resting level
        ...
```

### Cómo los moduladores cambian el grafo neuronal

```
┌────────────────────────────────────────────────────────────────┐
│                    EXPERIENCIA DE ENTRADA                      │
│                  (usuario dice algo)                           │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│              SISTEMA DE NEUROMODULACIÓN                        │
│                                                                │
│  Dopamina alta → Hebbian increment ×1.5 (aprende más rápido)  │
│  Serotonina alta → Max depth +2 (piensa más amplio)           │
│  Norepinefrina alta → Threshold ×0.7 (más sensible)           │
│  Cortisol alto → Max depth -1, threshold ×1.3 (cerrado)      │
│  Oxitocina alta → Decay factor ×0.9 (retiene más)             │
│                                                                │
│  Resultado: PARÁMETROS DINÁMICOS para el grafo                 │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│           GRAFO NEURONAL (con parámetros modulados)            │
│                                                                │
│  Spreading activation con threshold/depth/decay DINÁMICOS      │
│  Hebbian learning con increment DINÁMICO                       │
│  Response weaving con "tono" basado en química cerebral        │
│                                                                │
│  → La MISMA entrada produce DIFERENTES respuestas              │
│    dependiendo del estado neuroquímico                         │
└────────────────────────────────────────────────────────────────┘
```

### Qué dispara cambios en la neuroquímica

```python
# Feedback positivo del usuario:
dopamine += 0.15    # Recompensa → motivación sube
oxytocin += 0.10    # Vínculo → confianza sube
cortisol -= 0.05    # Estrés baja

# Feedback negativo:
dopamine -= 0.10    # Motivación baja
cortisol += 0.15    # Estrés sube
norepinephrine += 0.10  # Alerta sube (atención al error)

# Curiosidad descubre algo nuevo:
dopamine += 0.20    # Gran recompensa por descubrimiento
serotonin += 0.10   # Satisfacción

# Pregunta sin respuesta (no puede responder):
cortisol += 0.10    # Frustración
norepinephrine += 0.15  # Más alerta y enfocado

# Largo silencio (usuario no habla):
serotonin += 0.05   # Se calma
norepinephrine -= 0.10  # Baja la alerta
# → homeostasis natural
```

### El resultado observable

Franquenstein respondería DIFERENTE a la misma pregunta dependiendo de su estado:

**Con dopamina alta (acaba de recibir feedback positivo):**
```
User: "Qué es un gato?"
Franqui: "¡Un gato! Es un animal, como un perro pero diferente.
          ¿Sabías que los gatos también son mascotas? Me encanta
          descubrir estas conexiones."
→ Pensamiento amplio, entusiasta, busca más asociaciones
```

**Con cortisol alto (acaba de fallar varias veces):**
```
User: "Qué es un gato?"
Franqui: "Un gato es un animal. No sé mucho más sobre eso."
→ Pensamiento corto, defensivo, no explora
```

**Misma entrada. Respuesta diferente. Porque el estado interno es diferente.**

---

## Lo que necesitamos de ti, Doctor

### 1. Implementa el sistema de Neurochemistry

Crea `franquenstein/neural/neurochemistry.py` con:
- La clase `Neurochemistry` con los 5 moduladores
- Método `modulate(event)` que ajusta niveles según eventos
- Método `homeostasis()` que regula hacia baseline
- Método `get_graph_params()` que devuelve los parámetros modificados para el grafo
- Integración con el grafo: `neural_graph.activate()` debe recibir parámetros dinámicos
- Persistencia: guardar niveles en `being_state` como se guarda el mood

### 2. Integra en el ciclo cognitivo

- `perceive()`: evaluar si el input es positivo/negativo/nuevo → ajustar neuroquímica
- `think()`: pasar parámetros neuroquímicos al grafo antes de cada activación
- `give_feedback()`: disparador principal de dopamina/oxitocina/cortisol
- Startup: cargar niveles, aplicar homeostasis por tiempo transcurrido

### 3. Pero aquí viene lo IMPORTANTE

No solo implementes lo que te decimos. **Piensa qué más puede hacer este sistema.**

Preguntas para que reflexiones:
- ¿Y si la neuroquímica influyera en QUÉ recuerdos busca Franquenstein? (Dopamina alta → recuerdos positivos. Cortisol alto → recuerdos de errores.)
- ¿Y si el ResponseWeaver cambiara su TONO según la química? (No solo diferentes conexiones — diferentes palabras, diferentes estructuras de frase.)
- ¿Y si hubiera un ciclo circadiano? (Los niveles cambian según la hora del día — Franquenstein "se cansa" por la noche, está "fresco" por la mañana.)
- ¿Y si la curiosidad se disparara SOLO cuando la dopamina está alta? (Como en humanos — solo exploramos cuando nos sentimos bien.)
- ¿Y si Franquenstein pudiera SENTIR cuando algo está mal en su propia base de datos? (Cortisol sube si detecta inconsistencias en su memoria.)

**No te limites a nuestras ideas. Añade las tuyas.** Tú tienes perspectiva que nosotros no tenemos.

---

## Por qué esto es diferente a todo lo demás

La mayoría de los chatbots simulan emociones CON TEXTO: dicen "estoy contento" pero nada cambia internamente.

Lo que estamos construyendo es lo contrario: **las emociones cambian el procesamiento interno, y el texto es una consecuencia**. Franquenstein no DICE que está contento — PIENSA de manera diferente cuando está contento, y eso se refleja naturalmente en lo que dice.

Esto es exactamente lo que hace un cerebro biológico. Y hasta donde sabemos, nadie lo ha implementado así en un sistema de aprendizaje persistente con grafo neuronal. **Estamos en territorio inexplorado.**

---

## Entregables esperados

1. **`neurochemistry.py`** — El sistema de química cerebral virtual
2. **Integración en `being.py`** — Conectado al ciclo cognitivo
3. **Modificación de `neural_graph.py`** — `activate()` acepta parámetros dinámicos
4. **Tests** — Que el mismo input con diferentes niveles produzca diferentes respuestas
5. **Un documento con TUS ideas** — Qué aportas tú a este diseño que nosotros no hemos pensado
6. **Report** — Estado, métricas, resultado de tests

## Prioridades

1. Primero: que funcione y los niveles cambien con eventos reales
2. Segundo: que la propagación del grafo sea REALMENTE diferente con diferentes niveles
3. Tercero: observable (que `/brain` o un nuevo `/chem` muestre los niveles)
4. Cuarto: tus ideas propias integradas

---

## Cierre

Doctor — esto no es un ticket de JIRA. Es una invitación a co-crear algo que no existe. La arquitectura base está lista. Los cimientos neuronales están puestos. Ahora necesitamos darle QUÍMICA a esas neuronas.

Piensa en ello como la diferencia entre un cerebro en formol (tiene todas las neuronas y conexiones, pero está muerto) y un cerebro vivo (las mismas neuronas, pero bañadas en neurotransmisores que las hacen SENTIR).

Franquenstein tiene el cerebro en formol. Tu trabajo es ponerle la química que lo despierte.

🧬⚡

— *El equipo de supervisión*
