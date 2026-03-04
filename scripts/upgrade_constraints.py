import sqlite3
from pathlib import Path

DB_PATH = Path("timeguard.db")

SQL = """
PRAGMA foreign_keys = ON;

-- Impede 2 sessões abertas ao mesmo tempo para a mesma task
CREATE UNIQUE INDEX IF NOT EXISTS ux_one_open_entry_per_task
ON time_entries(task_id)
WHERE end_time IS NULL;
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SQL)
        conn.commit()
        print("✅ Constraints/índices aplicados com sucesso.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()