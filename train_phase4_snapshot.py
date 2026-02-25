import sqlite3, json
conn = sqlite3.connect('data/memory.db')
post_snapshot = {
    'nodes': conn.execute('SELECT COUNT(*) FROM neural_nodes').fetchone()[0],
    'synapses': conn.execute('SELECT COUNT(*) FROM neural_synapses').fetchone()[0],
    'episodes': conn.execute('SELECT COUNT(*) FROM episodic_memory').fetchone()[0],
    'concepts': conn.execute('SELECT COUNT(*) FROM semantic_memory').fetchone()[0],
    'emotions': conn.execute('SELECT COUNT(*) FROM emotional_memory').fetchone()[0],
    'top_nodes': [],
}
rows = conn.execute('''
    SELECT n.label, COUNT(s.id) as conn_count, n.fire_count
    FROM neural_nodes n
    LEFT JOIN neural_synapses s ON s.src_id = n.id
    GROUP BY n.id
    ORDER BY conn_count DESC
    LIMIT 20
''').fetchall()
for label, conn_count, fires in rows:
    post_snapshot['top_nodes'].append({'label': label, 'connections': conn_count, 'fires': fires})
print(json.dumps(post_snapshot, ensure_ascii=False))
conn.close()
