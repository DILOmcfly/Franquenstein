import time, sqlite3
from franquenstein.being import Being
from main import InnerWorld, VoiceEngine
from franquenstein.neural import NeuralGraph, ResponseWeaver

being = Being()
voice = VoiceEngine()
last_interaction = [time.time() - 600]
inner = InnerWorld(being=being, voice=voice, last_interaction_ref=last_interaction)

own_conn = sqlite3.connect(str(being.memory._db_path))
own_conn.execute('PRAGMA journal_mode=WAL')
own_neural = NeuralGraph(own_conn)
own_weaver = ResponseWeaver(own_neural)

thoughts=[]
start=time.time()
while time.time()-start < 60:
    t=inner.inner_thought_step(idle_seconds=time.time()-start+600, neural=own_neural, weaver=own_weaver)
    if t:
        thoughts.append(t)
    time.sleep(5)

print({'inner_thoughts_count': len(thoughts), 'thoughts': thoughts[-8:]})
own_conn.close(); being.shutdown()
