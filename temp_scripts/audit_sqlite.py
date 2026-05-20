"""
Auditoría completa del esquema SQLite de structural_embeddings.
Muestra: columnas, índices, constraints, PK, y filas de muestra.
"""
import sqlite3, json

conn = sqlite3.connect('runs/math_search.db')

# 1. DDL completo de la tabla
print("=== CREATE SQL ===")
row = conn.execute(
    "SELECT sql FROM sqlite_master WHERE type='table' AND name='structural_embeddings'"
).fetchone()
print(row[0] if row else "TABLE NOT FOUND")
print()

# 2. PRAGMA columns
print("=== PRAGMA table_info ===")
cols = conn.execute("PRAGMA table_info(structural_embeddings)").fetchall()
print(f"{'cid':<4} {'name':<22} {'type':<12} {'notnull':<8} {'dflt_value':<12} {'pk':<4}")
print("-" * 65)
for c in cols:
    print(f"{c[0]:<4} {c[1]:<22} {c[2]:<12} {c[3]:<8} {str(c[4]):<12} {c[5]:<4}")
col_names = [c[1] for c in cols]
print()

# 3. Indexes
print("=== PRAGMA index_list ===")
idxs = conn.execute("PRAGMA index_list(structural_embeddings)").fetchall()
if idxs:
    for idx in idxs:
        print(f"  Index: {idx[1]}  unique={idx[2]}  origin={idx[3]}")
        info = conn.execute(f"PRAGMA index_info('{idx[1]}')").fetchall()
        for ii in info:
            print(f"    col[{ii[0]}]: {ii[2]}")
else:
    print("  (no indexes)")
print()

# 4. Check presence of noise_level and seed
print("=== COLUMN PRESENCE ===")
for needed in ['noise_level', 'seed']:
    present = needed in col_names
    print(f"  {needed:<15}: {'PRESENT [OK]' if present else 'MISSING [!!]'}")
print()

# 5. Row count and sample
print("=== ROW SAMPLE (first 5) ===")
rows = conn.execute("SELECT * FROM structural_embeddings LIMIT 5").fetchall()
header = [c[1] for c in cols]
print("  " + " | ".join(f"{h:<18}" for h in header))
for r in rows:
    print("  " + " | ".join(f"{str(v):<18}" for v in r))
print(f"\n  Total rows: {conn.execute('SELECT COUNT(*) FROM structural_embeddings').fetchone()[0]}")

conn.close()
