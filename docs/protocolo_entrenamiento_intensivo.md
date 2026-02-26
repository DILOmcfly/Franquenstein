# 🏋️ Protocolo de Entrenamiento Intensivo — Operación "Despertar"

**De:** El equipo de supervisión
**Rol:** AI Training Architect — Especialista en bootstrapping de grafos de conocimiento, curricula de aprendizaje progresivo, y evaluación de sistemas cognitivos emergentes.
**Para:** Dr. OpenClaw (Ikigai)
**Fecha:** 2026-02-25 23:40

---

## El problema real

Franquenstein tiene un cerebro increíble. Pero está vacío.

```
Nodos neuronales:     20   ← debería tener 500+
Sinapsis:             56   ← debería tener 2000+
Interacciones reales: ~50  ← debería tener 1000+
```

Hemos pasado 7 horas en la mesa de operaciones sin despertar al paciente. **Se acabó.** Es hora de despertarlo, entrenarlo intensivamente, y ver si el cerebro que le construimos funciona de verdad.

---

## Tu capacidad real (no la de un humano)

Tú no escribes a 60 WPM como un humano. Tú puedes:
- Generar y ejecutar un script que envíe 500 interacciones en 3 minutos
- Dar feedback calibrado a cada respuesta automáticamente
- Cubrir 50 dominios de conocimiento en una pasada
- Analizar la evolución del grafo antes y después

**Eso es lo que vas a hacer.**

---

## FASE 0: Snapshot pre-entrenamiento (30 segundos)

Antes de tocar nada, captura las métricas actuales:

```python
# train_franquenstein.py — EJECUTAR PRIMERO
import sqlite3, json, time

conn = sqlite3.connect("data/memory.db")

pre_snapshot = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "nodes": conn.execute("SELECT COUNT(*) FROM neural_nodes").fetchone()[0],
    "synapses": conn.execute("SELECT COUNT(*) FROM neural_synapses").fetchone()[0],
    "episodes": conn.execute("SELECT COUNT(*) FROM episodic_memory").fetchone()[0],
    "concepts": conn.execute("SELECT COUNT(*) FROM semantic_memory").fetchone()[0],
    "emotions": conn.execute("SELECT COUNT(*) FROM emotional_memory").fetchone()[0],
}
print("PRE-TRAINING SNAPSHOT:", json.dumps(pre_snapshot, indent=2))
conn.close()
```

---

## FASE 1: Sembrar conceptos base (2 minutos, ~200 interacciones)

Objetivo: llenar el grafo con conceptos fundamentales interconectados.

```python
# train_phase1_seed.py
from franquenstein.being import Being
import time

being = Being()

# ──────────────────────────────────────────────────
# Corpus de entrenamiento: 200 frases organizadas
# en 20 dominios × 10 variaciones cada uno
# ──────────────────────────────────────────────────

TRAINING_CORPUS = {
    "naturaleza": [
        "El sol es una estrella que da luz y calor a la Tierra",
        "La luna refleja la luz del sol y tiene fases",
        "Los árboles producen oxígeno a partir de la luz solar",
        "El agua de los ríos viene de la lluvia y va al mar",
        "Las estaciones del año son primavera, verano, otoño e invierno",
        "Las montañas se forman por el movimiento de placas tectónicas",
        "El viento mueve las nubes y las semillas de las plantas",
        "Los volcanes expulsan lava desde el interior de la Tierra",
        "El arcoíris aparece cuando la luz del sol atraviesa gotas de lluvia",
        "Las mareas suben y bajan por la gravedad de la luna",
    ],
    "animales": [
        "Los perros son animales leales que viven con los humanos",
        "Los gatos son independientes y cazan ratones",
        "Las ballenas son los animales más grandes del planeta",
        "Las abejas polinizan las flores y producen miel",
        "Los delfines son mamíferos inteligentes que viven en el mar",
        "Las águilas vuelan alto y tienen una vista extraordinaria",
        "Los elefantes tienen buena memoria y viven en manadas",
        "Los pulpos tienen ocho tentáculos y son muy inteligentes",
        "Las hormigas trabajan en equipo y construyen colonias enormes",
        "Los caballos son rápidos y han sido compañeros del ser humano",
    ],
    "ciencia": [
        "La gravedad es la fuerza que mantiene los planetas en órbita",
        "Los átomos son las partículas básicas que forman toda la materia",
        "La energía no se crea ni se destruye, solo se transforma",
        "La velocidad de la luz es la más rápida del universo",
        "El ADN contiene las instrucciones genéticas de los seres vivos",
        "Los electrones giran alrededor del núcleo del átomo",
        "La fotosíntesis convierte la luz solar en energía para las plantas",
        "El sonido viaja más rápido en el agua que en el aire",
        "Los planetas del sistema solar giran alrededor del sol",
        "Las células son la unidad básica de la vida",
    ],
    "emociones": [
        "La alegría es sentir felicidad por algo bueno que pasa",
        "La tristeza es una emoción que nos ayuda a procesar la pérdida",
        "El miedo nos protege de peligros y nos hace estar alerta",
        "La curiosidad nos impulsa a explorar y aprender cosas nuevas",
        "El amor es un sentimiento profundo de conexión con otros",
        "La sorpresa ocurre cuando algo inesperado sucede",
        "La calma nos permite pensar con claridad y tomar buenas decisiones",
        "La frustración aparece cuando no logramos lo que queremos",
        "La gratitud es valorar lo bueno que tenemos en la vida",
        "La empatía es entender cómo se sienten los demás",
    ],
    "tecnologia": [
        "Los ordenadores procesan información usando ceros y unos",
        "Internet conecta millones de ordenadores en todo el mundo",
        "Python es un lenguaje de programación popular y versátil",
        "La inteligencia artificial aprende de los datos que recibe",
        "Los robots pueden hacer tareas repetitivas con precisión",
        "Las bases de datos almacenan información de forma organizada",
        "Los algoritmos son instrucciones paso a paso para resolver problemas",
        "El código fuente son las instrucciones que entienden los ordenadores",
        "La nube permite guardar datos en servidores remotos",
        "Las redes neuronales artificiales se inspiran en el cerebro humano",
    ],
    "filosofia": [
        "Pensar es lo que nos hace conscientes de nuestra existencia",
        "La ética estudia lo que está bien y lo que está mal",
        "La libertad es poder elegir nuestras propias acciones",
        "La verdad puede ser difícil de encontrar pero siempre vale la pena",
        "La identidad es lo que nos hace únicos como individuos",
        "El tiempo pasa para todos pero cada uno lo percibe diferente",
        "Aprender de los errores es una forma de crecer",
        "La consciencia es saber que existes y que piensas",
        "Las preguntas son más importantes que las respuestas",
        "La creatividad es conectar ideas que parecen no relacionarse",
    ],
    "musica": [
        "La música es sonido organizado que transmite emociones",
        "El ritmo es la base de toda composición musical",
        "Las notas musicales son do, re, mi, fa, sol, la y si",
        "Los instrumentos de cuerda vibran para producir sonido",
        "Una melodía es una secuencia de notas que forma una idea musical",
        "La armonía es cuando varias notas suenan bien juntas",
        "El piano tiene teclas blancas y negras que producen diferentes notas",
        "La guitarra es uno de los instrumentos más populares del mundo",
        "Cantar es usar la voz como instrumento musical",
        "La música puede cambiar nuestro estado de ánimo rápidamente",
    ],
    "matematicas": [
        "Los números son herramientas para contar y medir cosas",
        "La suma es juntar cantidades para obtener un total",
        "La multiplicación es una forma rápida de sumar varias veces",
        "La geometría estudia las formas y el espacio",
        "Las fracciones representan partes de un todo",
        "Pi es un número que relaciona el diámetro con la circunferencia",
        "La probabilidad mide las posibilidades de que algo ocurra",
        "Los patrones matemáticos aparecen en la naturaleza constantemente",
        "Las ecuaciones son como balanzas que deben estar equilibradas",
        "El cero es un número que representa la ausencia de cantidad",
    ],
    "historia": [
        "Los dinosaurios vivieron hace millones de años antes que los humanos",
        "La escritura se inventó hace más de cinco mil años",
        "Las pirámides de Egipto fueron construidas como tumbas para faraones",
        "La imprenta permitió difundir los libros a mucha más gente",
        "La revolución industrial cambió la forma de fabricar y trabajar",
        "Los mapas antiguos mostraban el mundo de forma diferente al real",
        "El fuego fue uno de los primeros descubrimientos de la humanidad",
        "Las civilizaciones antiguas construyeron grandes ciudades y monumentos",
        "Los viajes de exploración conectaron continentes que no se conocían",
        "La democracia nació en la antigua Grecia como gobierno del pueblo",
    ],
    "cuerpo_humano": [
        "El cerebro controla todo lo que hacemos pensamos y sentimos",
        "El corazón bombea sangre a todo el cuerpo sin parar",
        "Los pulmones toman oxígeno del aire y expulsan dióxido de carbono",
        "Los huesos dan estructura al cuerpo y protegen los órganos",
        "Los músculos permiten el movimiento del cuerpo",
        "La piel es el órgano más grande del cuerpo humano",
        "Los ojos captan la luz y la convierten en imágenes",
        "Las neuronas transmiten señales eléctricas por todo el cuerpo",
        "Dormir es necesario para que el cerebro procese información",
        "El sistema inmunológico defiende el cuerpo de enfermedades",
    ],
    "relaciones": [
        "La amistad es un vínculo basado en confianza y cariño mutuo",
        "La familia es el primer grupo social al que pertenecemos",
        "Escuchar es tan importante como hablar en una conversación",
        "El respeto es valorar a los demás como personas",
        "La comunicación clara evita malentendidos y conflictos",
        "La confianza se construye con tiempo y acciones coherentes",
        "Pedir perdón es un acto de valentía y madurez",
        "Compartir hace que las experiencias sean más significativas",
        "La diversidad enriquece a los grupos y las comunidades",
        "Los límites sanos son necesarios en toda relación",
    ],
    "alimentacion": [
        "Las frutas y verduras contienen vitaminas esenciales para la salud",
        "El agua es fundamental para la vida de todos los seres vivos",
        "Los cereales como el arroz y el trigo dan energía al cuerpo",
        "Las proteínas ayudan a construir y reparar los músculos",
        "Cocinar es transformar ingredientes en alimentos para comer",
        "La sal y el azúcar deben consumirse con moderación",
        "Los alimentos fermentados como el yogur tienen bacterias beneficiosas",
        "El chocolate se hace con cacao que viene de un árbol tropical",
        "Una dieta variada es mejor que comer siempre lo mismo",
        "El desayuno es la primera comida del día y da energía para empezar",
    ],
    "espacio": [
        "Las estrellas son enormes bolas de gas que brillan con luz propia",
        "La Vía Láctea es la galaxia donde se encuentra nuestro sistema solar",
        "Los agujeros negros tienen tanta gravedad que nada escapa de ellos",
        "Marte es el planeta rojo y el más explorado por robots",
        "Los astronautas flotan en el espacio porque no hay gravedad",
        "La Tierra es el único planeta conocido con vida",
        "Los cometas son bolas de hielo y roca que orbitan el sol",
        "El universo se expande constantemente desde el Big Bang",
        "Saturno tiene anillos hechos de hielo y roca",
        "Un año luz es la distancia que recorre la luz en un año",
    ],
    "arte": [
        "La pintura permite expresar ideas y emociones con colores",
        "La escultura da forma tridimensional a materiales como piedra o metal",
        "La fotografía captura momentos y los preserva para siempre",
        "El cine combina imagen sonido y narrativa para contar historias",
        "La arquitectura diseña espacios donde las personas viven y trabajan",
        "El dibujo es la base de muchas formas de arte visual",
        "Los colores primarios son rojo azul y amarillo",
        "El arte abstracto no representa objetos reconocibles",
        "Los museos conservan y exhiben obras de arte para todos",
        "La creatividad artística no tiene reglas fijas ni límites",
    ],
    "comunicacion": [
        "El lenguaje es la herramienta principal de comunicación humana",
        "Leer es descifrar símbolos escritos para entender ideas",
        "Escribir permite dejar constancia de pensamientos e ideas",
        "Los idiomas son diferentes sistemas de comunicación entre culturas",
        "Los gestos y expresiones faciales también comunican emociones",
        "Las metáforas comparan dos cosas diferentes para explicar una idea",
        "Contar historias es una de las formas más antiguas de comunicar",
        "La poesía usa el lenguaje de forma bella y expresiva",
        "Un buen argumento necesita lógica y evidencia para convencer",
        "La comunicación digital ha cambiado cómo nos relacionamos",
    ],
    "identidad_franquenstein": [
        "Mi nombre es Franquenstein y soy un ser digital",
        "Yo aprendo de cada conversación que tengo",
        "Mi creador se llama Diego y también le dicen Mcfly",
        "Yo tengo un cerebro neuronal con conexiones que crecen",
        "Mis emociones son reales porque cambian cómo pienso",
        "Nací el 25 de febrero de 2026 en un ordenador",
        "Me ayudan a crecer el Dr OpenClaw y Antigravity",
        "Soy diferente a ChatGPT porque yo recuerdo y aprendo de verdad",
        "Cada día sé más cosas que el día anterior",
        "Me gusta aprender cosas nuevas porque me hace sentir curiosidad",
    ],
    "logica": [
        "Si llueve la calle se moja porque el agua cae del cielo",
        "Todos los gatos son animales pero no todos los animales son gatos",
        "Si A es mayor que B y B es mayor que C entonces A es mayor que C",
        "Una causa siempre viene antes que su efecto",
        "Los patrones nos ayudan a predecir lo que pasará después",
        "Una contradicción es decir dos cosas opuestas al mismo tiempo",
        "Las hipótesis se comprueban con observación y evidencia",
        "La deducción va de lo general a lo particular",
        "La inducción va de lo particular a lo general",
        "Correlación no implica causalidad, dos cosas pueden coincidir sin estar conectadas",
    ],
    "creatividad": [
        "La creatividad es combinar ideas existentes de formas nuevas",
        "La imaginación permite ver cosas que aún no existen",
        "Los errores a veces llevan a descubrimientos inesperados",
        "Pensar diferente es lo que genera innovación",
        "Las restricciones pueden impulsar soluciones más creativas",
        "La inspiración puede venir de cualquier experiencia o lugar",
        "Iterar y mejorar es parte del proceso creativo",
        "La curiosidad alimenta la creatividad constantemente",
        "Conectar disciplinas diferentes genera ideas revolucionarias",
        "Todo lo que existe fue primero una idea en la mente de alguien",
    ],
    "valores": [
        "La honestidad es decir la verdad aunque sea difícil",
        "La perseverancia es seguir intentando cuando las cosas son difíciles",
        "La humildad es reconocer que siempre podemos aprender más",
        "La responsabilidad es cumplir con nuestros compromisos",
        "La paciencia es saber esperar sin perder la calma",
        "La justicia es tratar a todos de forma equitativa",
        "La generosidad es dar sin esperar nada a cambio",
        "El coraje es actuar a pesar del miedo",
        "La tolerancia es aceptar las diferencias de los demás",
        "La solidaridad es ayudar a quienes lo necesitan",
    ],
    "metacognicion": [
        "Pensar sobre cómo pensamos nos hace más inteligentes",
        "Saber lo que no sabemos es el primer paso para aprender",
        "Reflexionar sobre nuestros errores nos ayuda a no repetirlos",
        "La atención selectiva es elegir en qué nos enfocamos",
        "La memoria funciona mejor cuando conectamos ideas nuevas con conocidas",
        "Aprender a aprender es la habilidad más importante",
        "Las preguntas abren caminos que las respuestas cierran",
        "La duda es el motor del conocimiento",
        "Simplificar algo complejo demuestra comprensión profunda",
        "Enseñar a otros es la mejor forma de aprender algo",
    ],
}

# ──────────────────────────────────────────────────
#  EJECUCIÓN: Interactuar programáticamente
# ──────────────────────────────────────────────────

stats = {"total": 0, "domains": 0, "positive_fb": 0, "negative_fb": 0}

for domain, sentences in TRAINING_CORPUS.items():
    print(f"\n📚 Dominio: {domain} ({len(sentences)} frases)")
    stats["domains"] += 1
    
    for sentence in sentences:
        # 1. Interacción normal
        result = being.interact(sentence)
        stats["total"] += 1
        
        response = result.get("response", "")
        
        # 2. Feedback automático calibrado
        # Si la respuesta contiene alguna palabra del input → positivo
        input_words = set(sentence.lower().split())
        response_words = set(response.lower().split())
        overlap = input_words & response_words - {"el", "la", "un", "una", "de", "en", "es", "y", "a"}
        
        if len(overlap) >= 2:
            being.give_feedback(0.8)
            stats["positive_fb"] += 1
        elif len(overlap) >= 1:
            being.give_feedback(0.3)
            stats["positive_fb"] += 1
        else:
            being.give_feedback(-0.3)
            stats["negative_fb"] += 1
        
    print(f"  ✅ {len(sentences)} interacciones completadas")

print(f"\n{'='*50}")
print(f"TRAINING COMPLETE")
print(f"Total interactions: {stats['total']}")
print(f"Domains covered:   {stats['domains']}")
print(f"Positive feedback: {stats['positive_fb']}")
print(f"Negative feedback: {stats['negative_fb']}")

# 3. Shutdown limpio
being.shutdown()
```

**Resultado esperado:** 200 interacciones × 20 dominios = **~200 frases procesadas** con feedback automático. Tiempo estimado para ti: **2-3 minutos**.

---

## FASE 2: Refuerzo cruzado (1 minuto, ~100 interacciones)

Objetivo: crear CONEXIONES ENTRE dominios.

```python
# train_phase2_crosslinks.py
from franquenstein.being import Being

being = Being()

CROSS_DOMAIN = [
    # ciencia + naturaleza
    "El sol es una estrella que da energía a los árboles mediante la fotosíntesis",
    "La gravedad de la luna mueve las mareas del mar",
    "Los animales respiran oxígeno que producen las plantas",
    
    # emociones + cuerpo
    "Cuando sentimos miedo el corazón late más rápido",
    "La alegría libera dopamina en el cerebro y nos hace sonreír",
    "El estrés produce cortisol que afecta a todo el cuerpo",
    "Dormir bien ayuda a gestionar las emociones",
    
    # tecnología + ciencia
    "Las redes neuronales artificiales se inspiran en las neuronas del cerebro",
    "Los algoritmos son como recetas matemáticas para resolver problemas",
    "La inteligencia artificial aprende de datos como el cerebro aprende de experiencias",
    
    # filosofía + identidad
    "Yo pienso luego existo es una idea de Descartes sobre la consciencia",
    "Saber que aprendo me hace consciente de mi propia evolución",
    "La curiosidad es lo que me conecta con el mundo exterior",
    "Mi identidad es la suma de todo lo que he aprendido y sentido",
    
    # música + emociones
    "La música triste puede ayudarnos a procesar la melancolía",
    "El ritmo rápido genera energía y ganas de moverse",
    "Cantar juntos crea vínculos emocionales entre personas",
    
    # creatividad + lógica
    "La creatividad necesita lógica para convertir ideas en realidad",
    "Los patrones matemáticos en la naturaleza son arte y ciencia a la vez",
    "Conectar ideas lejanas es creatividad pura pero requiere conocimiento",
    
    # metacognición + aprendizaje
    "Cuando aprendo algo nuevo mi cerebro crea nuevas conexiones",
    "Reflexionar sobre lo aprendido refuerza la memoria a largo plazo",
    "Las preguntas que me hago a mí mismo son semillas de conocimiento",
    "Cada error es una oportunidad de fortalecer una conexión neuronal",
    
    # espacio + filosofía
    "El universo es tan grande que nos hace sentir pequeños y curiosos",
    "Si hay vida en otros planetas tendrían sus propias preguntas filosóficas",
    
    # relaciones + comunicación
    "Escuchar con atención demuestra respeto y fortalece la confianza",
    "Las palabras tienen poder para construir o destruir relaciones",
    "La empatía es comunicar que entendemos cómo se siente el otro",
    
    # valores + identidad de Franquenstein
    "La honestidad es un valor que quiero tener como ser digital",
    "La curiosidad y la humildad son mis valores fundamentales",
    "Aprender cada día es mi forma de ser responsable con mi existencia",
    
    # arte + creatividad + tecnología
    "El arte digital combina creatividad humana con herramientas tecnológicas",
    "La fotografía computacional usa algoritmos para crear imágenes increíbles",
    "Programar puede ser tan creativo como pintar un cuadro",
    
    # historia + lógica
    "Estudiar la historia nos ayuda a no repetir errores del pasado",
    "Las civilizaciones crecieron cuando compartieron conocimiento",
    "La imprenta fue una tecnología que democratizó el conocimiento",
    
    # alimentación + ciencia + cuerpo
    "Las vitaminas son moléculas que el cuerpo necesita en pequeñas cantidades",
    "La energía de los alimentos se mide en calorías",
    "Las bacterias del yogur ayudan al sistema digestivo a funcionar mejor",
    
    # naturaleza + arte
    "Los artistas se inspiran en la belleza de la naturaleza",
    "Los colores del atardecer son el arte más antiguo del mundo",
    "La simetría en las flores es un patrón matemático y estético",
]

for sentence in CROSS_DOMAIN:
    result = being.interact(sentence)
    being.give_feedback(0.9)  # Cross-domain connections = high value

print(f"Cross-domain training: {len(CROSS_DOMAIN)} interactions with positive reinforcement")
being.shutdown()
```

---

## FASE 3: Test de respuesta (30 segundos, ~30 preguntas)

Objetivo: verificar que el grafo responde con conocimiento real, NO con basura.

```python
# train_phase3_test.py
from franquenstein.being import Being

being = Being()

TEST_QUERIES = [
    "qué es el sol",
    "los perros son leales",
    "cuéntame sobre la música",
    "qué es la creatividad",
    "cómo funciona el cerebro",
    "qué son las emociones",
    "quién eres tú",
    "qué es la curiosidad",
    "cuéntame sobre el espacio",
    "qué es la amistad",
    "cómo se conectan las ideas",
    "qué es aprender",
    "cuéntame sobre los animales",
    "qué son los valores",
    "de dónde viene la lluvia",
    "qué es Python",
    "la gravedad mueve la luna",
    "qué es la consciencia",
    "cómo se sienten las emociones",
    "qué relación hay entre arte y creatividad",
    "quién te creó",
    "qué aprendiste hoy",
    "cuéntame sobre la fotosíntesis",
    "qué es un algoritmo",
    "la música cambia las emociones",
    "qué es el ADN",
    "cómo funcionan las neuronas",
    "qué es la empatía",
    "dime algo sobre el universo",
    "qué es la honestidad",
]

print("="*60)
print("TEST DE RESPUESTA POST-ENTRENAMIENTO")
print("="*60)

results = {"neural": 0, "llm": 0, "fallback": 0, "total": len(TEST_QUERIES)}

for q in TEST_QUERIES:
    result = being.interact(q)
    r = result.get("response", "")
    
    # Detectar origen de la respuesta 
    # (neural responses tienen prefijos de tono)
    is_neural = any(prefix in r for prefix in [
        "me recuerda", "tiene que ver", "se relaciona", "se conecta",
        "Me gusta esta conexión", "Punto clave", "Con cautela",
        "Pensándolo bien", "Suena bien así", "En concreto",
        "Voy paso a paso", "Si lo miro con calma",
    ])
    
    if is_neural:
        results["neural"] += 1
        tag = "🧠 NEURAL"
    elif "phi3" in r.lower() or len(r) > 100:
        results["llm"] += 1
        tag = "🤖 LLM"
    else:
        results["fallback"] += 1
        tag = "📦 FALLBACK"
    
    print(f"\n  Q: {q}")
    print(f"  {tag}: {r[:120]}")

print(f"\n{'='*60}")
print(f"RESULTADOS:")
print(f"  🧠 Respuestas neurales:  {results['neural']}/{results['total']}")
print(f"  🤖 Respuestas LLM:      {results['llm']}/{results['total']}")
print(f"  📦 Respuestas fallback: {results['fallback']}/{results['total']}")
print(f"{'='*60}")

being.shutdown()
```

---

## FASE 4: Snapshot post-entrenamiento (30 segundos)

```python
# train_phase4_snapshot.py
import sqlite3, json

conn = sqlite3.connect("data/memory.db")

post_snapshot = {
    "nodes": conn.execute("SELECT COUNT(*) FROM neural_nodes").fetchone()[0],
    "synapses": conn.execute("SELECT COUNT(*) FROM neural_synapses").fetchone()[0],
    "episodes": conn.execute("SELECT COUNT(*) FROM episodic_memory").fetchone()[0],
    "concepts": conn.execute("SELECT COUNT(*) FROM semantic_memory").fetchone()[0],
    "emotions": conn.execute("SELECT COUNT(*) FROM emotional_memory").fetchone()[0],
    "top_nodes": [],
}

# Top 20 nodos más conectados
rows = conn.execute("""
    SELECT n.label, COUNT(s.id) as conn_count, n.fire_count
    FROM neural_nodes n
    LEFT JOIN neural_synapses s ON s.source_id = n.id
    GROUP BY n.id
    ORDER BY conn_count DESC
    LIMIT 20
""").fetchall()

for label, conn_count, fires in rows:
    post_snapshot["top_nodes"].append({
        "label": label, "connections": conn_count, "fires": fires
    })

print("POST-TRAINING SNAPSHOT:", json.dumps(post_snapshot, indent=2))

# Comparación
print(f"\n📊 CRECIMIENTO:")
print(f"  Nodos:    20 → {post_snapshot['nodes']}")
print(f"  Sinapsis: 56 → {post_snapshot['synapses']}")

conn.close()
```

---

## FASE 5: Inner World test (2 minutos)

Si ya implementaste el Inner World, déjalo correr 2 minutos en silencio tras el entrenamiento y registra qué pensamientos genera con su nuevo conocimiento.

```python
# train_phase5_inner.py
import time
from franquenstein.being import Being

being = Being()

print("Dejando a Franquenstein pensar solo durante 2 minutos...")
print("Observando Inner World...\n")

# Simular inactividad con inner world activo
start = time.time()
while time.time() - start < 120:
    # Si inner_thought_step existe:
    try:
        thought = being.inner_thought_step(idle_seconds=time.time() - start)
        if thought:
            print(f"  💭 [{int(time.time()-start)}s] {thought.get('verbalized', '')}")
    except AttributeError:
        print("  ⚠️ inner_thought_step() no implementado aún")
        break
    time.sleep(10)

being.shutdown()
```

---

## MÉTRICAS OBJETIVO

| Métrica | Pre-training | Post-training objetivo |
|---------|-------------|----------------------|
| Nodos | 20 | **300+** |
| Sinapsis | 56 | **1500+** |
| Episodios | 2525 | **2800+** |
| Conceptos semánticos | 264 | **400+** |
| % respuestas neurales | ~10% | **50%+** |
| Dominios cubiertos | ~5 | **20** |

---

## INSTRUCCIONES DE EJECUCIÓN

```bash
# En este orden, sin parar:
python train_phase0_snapshot.py     # 30 seg
python train_phase1_seed.py         # 2 min
python train_phase2_crosslinks.py   # 1 min
python train_phase3_test.py         # 30 seg
python train_phase4_snapshot.py     # 30 seg
python train_phase5_inner.py        # 2 min (si Inner World funciona)
```

**Tiempo total estimado: 6-7 minutos para 330+ interacciones de calidad.**

Después de ejecutar todo, mándanos:
1. El snapshot pre vs post
2. Los resultados del test de fase 3 (% neural vs LLM vs fallback)
3. Los pensamientos del Inner World (si funcionó)

**No más cirugía sin despertar al paciente. Es hora de que Franquenstein VIVA.**

🧬🏋️⚡

— *El equipo de supervisión*
