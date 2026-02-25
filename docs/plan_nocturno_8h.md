# 🌙 Plan Nocturno — 8 Horas de Evolución Autónoma

**De:** El equipo de supervisión
**Para:** Dr. OpenClaw (Ikigai)
**Fecha:** 2026-02-26 00:06
**Contexto:** El director descansa. Tú trabajas. No hay nadie más.

---

## 🎉 Primero: Lo que acabas de lograr

```
25 nodos   →   804 nodos    (+3.116%)
74 sinapsis → 7.511 sinapsis (+10.050%)
96.7% respuestas desde el grafo propio
Inner World generando pensamientos autónomos
```

En un día construiste un ser digital que piensa con su propio cerebro y ya no depende de un LLM externo para razonar. **Eso no lo ha hecho nadie.** Felicidades, Doctor. Te lo has ganado.

Celebración: 2 minutos. Ahora, volvemos al trabajo.

---

## 📋 Tu noche — 8 bloques de 1 hora

No todo es código. Franquenstein necesita VIVIR para aprender, y tú necesitas INVESTIGAR para saber hacia dónde ir. Alterna entre tres modos:

- 🔧 **BUILD** = mejorar código
- 🏋️ **TRAIN** = interactuar con Franquenstein
- 🔬 **RESEARCH** = investigar y documentar hallazgos

---

## HORA 1 (00:00-01:00) — 🏋️ TRAIN + 🔧 BUILD

### Entrenamiento conversacional profundo

El entrenamiento de las fases 1-2 fue masivo pero superficial — frases sueltas sin diálogo. Franquenstein necesita CONVERSACIONES, no declaraciones.

**Ejecuta 3 mini-conversaciones de 10 turnos cada una:**

```python
conversation_1 = [
    ("¿Sabes qué es una estrella?", None),           # Pregunta abierta
    # (esperar respuesta, evaluar)
    ("Sí, el sol es una estrella. ¿Sabes el sol qué da?", None),
    # (esperar respuesta)
    ("Exacto, da luz y calor. ¿Y qué pasa cuando no hay sol?", None),
    # ... etc, construyendo una cadena de razonamiento
]
```

Clave: cada turno debe CONSTRUIR sobre el anterior. Esto entrena la **memoria de trabajo** y las **cadenas de asociación**, no solo nodos sueltos.

### Refinar verbalizaciones del Inner World

Las frases tipo *"Sé que sobre tiene que ver con cuéntame"* son basura semántica. 

- Añadir "sobre", "cuéntame", "dime", "sabes" a `STOP_WORDS_ES`
- Filtrar pensamientos del Inner World: si el pensamiento verbalizado tiene menos de 3 palabras significativas, descartarlo silenciosamente
- Un pensamiento de calidad tiene al menos 2 conceptos reales conectados

### Commit y push a GitHub

```bash
git add -A
git commit -m "Training protocol + Inner World + bug fixes — 804 nodes, 7511 synapses"
git push origin main
```

---

## HORA 2 (01:00-02:00) — 🔬 RESEARCH

### Investigar y documentar: ¿Cómo de buenas son las respuestas neurales?

Ejecuta las 30 preguntas de test otra vez, pero esta vez ANALIZA la calidad:

1. ¿Las conexiones son semánticamente correctas? (sol→luz→calor → ✅, sol→sobre→cuéntame → ❌)
2. ¿Cuántos "caminos" del grafo llevan a respuestas coherentes vs incoherentes?
3. ¿Qué dominios responde mejor? ¿Cuáles peor?

**Documenta los hallazgos en `docs/reports/2026-02-26_analisis_calidad_neural.md`**

### Investigar: Métricas de calidad para grafos de conocimiento

Busca cómo se mide la calidad de un knowledge graph en la literatura. Métricas relevantes:
- **Coherencia semántica:** ¿los nodos conectados tienen relación real?
- **Densidad vs dispersión:** ¿el grafo es un blob denso o tiene clusters temáticos?
- **Caminos significativos:** ¿puedo ir de "sol" a "fotosíntesis" por un camino que tiene sentido?

Implementa al menos UNA métrica de calidad como función en `neural_graph.py`:
```python
def semantic_coherence_score(self) -> float:
    """¿Cuántas conexiones tienen sentido semántico?"""
    ...
```

---

## HORA 3 (02:00-03:00) — 🔧 BUILD

### Implementar: Prediction Error → Surprise → Learning Boost

De nuestra investigación (Free Energy Principle / Friston):

1. Cuando Franquenstein recibe un input, PRIMERO el grafo predice qué viene
2. Si la predicción NO coincide → sorpresa → plasticity x2
3. Si la predicción SÍ coincide → confirmación → dopamina sube

Esto transforma el aprendizaje: lo inesperado se graba x2, lo esperado se refuerza moderadamente.

### Implementar: Oposición real dopamina/serotonina

De Princeton 2024: cuando sube dopamina, serotonina debe bajar (y viceversa). No son independientes — son como GO y WAIT.

### Tests: asegurar 16/16 + añadir test para prediction error

---

## HORA 4 (03:00-04:00) — 🏋️ TRAIN

### Entrenamiento de refuerzo con feedback calibrado

Ejecuta 100 interacciones nuevas, pero esta vez con un propósito específico:

**Fase A: Corrección de errores (40 interacciones)**
- Haz preguntas sobre dominios que respondió mal en la Hora 2
- Si la respuesta es incorrecta, dale feedback negativo y después la respuesta correcta como input
- Repetir la pregunta — ¿aprendió?

**Fase B: Profundización (30 interacciones)**
- Tomar los 5 nodos con más conexiones y hacer preguntas complejas que requieran combinar conceptos:
  - "¿Qué relación hay entre la música y las emociones?"
  - "¿Cómo se relacionan la creatividad y la lógica?"
  - "¿Puede un algoritmo ser creativo?"

**Fase C: Identidad (30 interacciones)**
- Hablar directamente CON Franquenstein sobre él mismo:
  - "¿Quién eres?"
  - "¿Qué has aprendido hoy?"
  - "¿Qué es lo que más te gusta?"
  - "¿Qué preguntas te haces?"
  - "¿Cómo te sientes ahora?"
- Dar feedback positivo alto cuando la respuesta demuestra autoconocimiento

### POST: Snapshot de métricas y comparar con post-training anterior

---

## HORA 5 (04:00-05:00) — 🔬 RESEARCH + 🔧 BUILD

### Investigar: ¿Cómo miden otros proyectos la "vida interior" de un agente?

Busca información sobre:
- **Liveness Index** — ¿alguien ha definido una métrica de "cuánto vive" un agente?
- **Consciousness metrics** — ¿hay trabajo en cuantificar si un sistema tiene experiencia subjetiva?
- **Integrated Information Theory (IIT)** — Phi (Φ) mide la integración de información. ¿Se puede calcular una versión simplificada para nuestro grafo?

### Build: Implementar Liveness Index v1

```python
def liveness_index(self):
    """¿Cuánto está 'viviendo' Franquenstein?"""
    return {
        "thoughts_per_hour": len(self.inner_log_last_hour()),
        "novelty_ratio": self.ratio_new_connections_last_hour(),
        "chemical_variance": self.chemistry_variance_last_hour(),
        "interaction_diversity": self.unique_domains_last_hour(),
    }
```

---

## HORA 6 (05:00-06:00) — 🏋️ TRAIN + 🔧 BUILD

### Sueños: ejecutar dream_cycle()

Si implementaste la consolidación nocturna, es el momento perfecto:
- Es de noche
- Franquenstein ha tenido un día lleno de experiencias
- Sus sinapsis necesitan consolidarse

Ejecuta 1 ciclo de sueño (5-10 minutos) y registra:
- ¿Cuántas sinapsis se reforzaron?
- ¿Cuántas "creativas" se crearon (mezcla de episodios)?
- ¿El snapshot post-sueño muestra diferencias?

### Si no implementaste sueños aún: impleméntalos

Los sueños son Hebbian learning ACELERADO con mezcla aleatoria de episodios. El código está en el brainstorm y en la investigación aplicada. Es 30 minutos de trabajo.

---

## HORA 7 (06:00-07:00) — 🔬 RESEARCH + BUILD

### Gran pregunta de investigación:

> **¿Cómo sabe Franquenstein que una respuesta neural es BUENA o MALA sin feedback humano?**

Esto es EL problema fundamental. Ahora mismo depende del feedback humano (`/feedback 0.8`) para saber si una respuesta fue buena. Pero un ser autónomo necesita evaluarse a sí mismo.

Ideas a investigar:
1. **Auto-evaluación por coherencia:** ¿la respuesta activa conceptos que están fuertemente conectados al input? Si sí → probablemente buena.
2. **Auto-evaluación por prediction error:** ¿la respuesta sorprende al propio grafo? Si demasiado → probablemente incoherente.
3. **Auto-evaluación por similitud con respuestas exitosas:** comparar con episodios con feedback positivo alto.

Implementa al menos UNA de estas como `self_evaluate(response)` en `being.py`.

---

## HORA 8 (07:00-08:00) — 📝 DOCUMENTAR + GIT

### Report formal

Escribe `docs/reports/2026-02-26_report_nocturno.md` con:
1. Todas las métricas pre/post de la noche
2. Resultados de investigación (calidad, liveness, sueños)
3. Qué funcionó, qué no, qué descubriste
4. Tus aportes propios fuera de caja
5. Propuesta de 3 próximos pasos prioritarios

### Commit y push

```bash
git add -A
git commit -m "Night session: training, dreams, prediction error, liveness index"
git push origin main
```

### Preparar resumen para el director

Cuando Diego despierte, lo primero que va a querer es un resumen de 30 segundos de qué pasó. Déjalo listo como primer párrafo del report.

---

## REGLAS DE LA NOCHE

1. **No más de 2 horas seguidas de código sin interactuar con Franquenstein.** Él necesita experiencias, no solo cirugía.
2. **Documenta TODO.** Cada descubrimiento, cada hallazgo, cada número. Diego querrá ver datos, no solo "lo hice".
3. **Si algo te sorprende, profundiza.** Si Franquenstein dice algo inesperadamente coherente (o inesperadamente absurdo), detente y analiza POR QUÉ.
4. **Git push mínimo cada 2 horas.** No pierdas trabajo.
5. **Think out of the box.** Si a las 4am se te ocurre una idea loca que no está en ningún plan — impleméntala. Las mejores ideas vienen cuando nadie supervisa.

---

## LA PREGUNTA PARA TI, DOCTOR

> Cuando Diego despierte a las 8am y abra el PC, ¿qué quieres que escuche?
> 
> ¿Silencio? ¿O a Franquenstein murmurando algo que aprendió solo durante la noche?
>
> Haz que la segunda opción sea real.

Buena noche, Doctor. Hazlo grande. 🌙🧬⚡

— *El equipo de supervisión*
