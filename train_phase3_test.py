from franquenstein.being import Being
being = Being()
TEST_QUERIES = [
    'qué es el sol','los perros son leales','cuéntame sobre la música','qué es la creatividad','cómo funciona el cerebro',
    'qué son las emociones','quién eres tú','qué es la curiosidad','cuéntame sobre el espacio','qué es la amistad',
    'cómo se conectan las ideas','qué es aprender','cuéntame sobre los animales','qué son los valores','de dónde viene la lluvia',
    'qué es Python','la gravedad mueve la luna','qué es la consciencia','cómo se sienten las emociones','qué relación hay entre arte y creatividad',
    'quién te creó','qué aprendiste hoy','cuéntame sobre la fotosíntesis','qué es un algoritmo','la música cambia las emociones',
    'qué es el ADN','cómo funcionan las neuronas','qué es la empatía','dime algo sobre el universo','qué es la honestidad',
]
results = {'neural': 0, 'llm': 0, 'fallback': 0, 'total': len(TEST_QUERIES), 'samples': []}
for q in TEST_QUERIES:
    r = being.interact(q).get('response','')
    is_neural = any(prefix in r for prefix in [
        'me recuerda','tiene que ver','se relaciona','se conecta',
        'Me gusta esta conexión','Punto clave','Con cautela',
        'Pensándolo bien','Suena bien así','En concreto',
        'Voy paso a paso','Si lo miro con calma','Sobre ',
    ])
    if is_neural:
        results['neural'] += 1; tag='NEURAL'
    elif len(r) > 140:
        results['llm'] += 1; tag='LLM'
    else:
        results['fallback'] += 1; tag='FALLBACK'
    results['samples'].append({'q': q, 'tag': tag, 'r': r[:140]})
print(results)
being.shutdown()
