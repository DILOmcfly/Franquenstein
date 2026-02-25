import sqlite3, json, time

conn = sqlite3.connect('data/memory.db')
pre_snapshot = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'nodes': conn.execute('SELECT COUNT(*) FROM neural_nodes').fetchone()[0],
    'synapses': conn.execute('SELECT COUNT(*) FROM neural_synapses').fetchone()[0],
    'episodes': conn.execute('SELECT COUNT(*) FROM episodic_memory').fetchone()[0],
    'concepts': conn.execute('SELECT COUNT(*) FROM semantic_memory').fetchone()[0],
    'emotions': conn.execute('SELECT COUNT(*) FROM emotional_memory').fetchone()[0],
}
print(json.dumps(pre_snapshot, ensure_ascii=False))
conn.close()
