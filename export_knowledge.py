import sqlite3
import json
import os

DB_PATH = os.path.join("runs", "math_search.db")
OUTPUT_FILE = "ATLAS_INSIGHTS.json"

def export_knowledge():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meta_insights'")
        if not cursor.fetchone():
            print("Error: Table 'meta_insights' does not exist in the database.")
            return

        cursor.execute("SELECT * FROM meta_insights")
        rows = cursor.fetchall()
        
        insights = []
        for row in rows:
            insight = dict(row)
            insights.append(insight)
            
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(insights, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully exported {len(insights)} insights to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error exporting knowledge: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    export_knowledge()
