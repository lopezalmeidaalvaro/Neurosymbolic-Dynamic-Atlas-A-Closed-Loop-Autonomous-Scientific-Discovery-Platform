import sqlite3
conn = sqlite3.connect('runs/math_search.db')
rows = conn.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
for r in rows:
    print(r[0])
    print()
conn.close()
