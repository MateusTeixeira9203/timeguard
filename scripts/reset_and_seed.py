import sqlite3
from pathlib import Path
import random

DB_PATH = Path("timeguard.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Limpa (ordem importa)
    cur.execute("DELETE FROM time_entries;")
    cur.execute("DELETE FROM tasks;")
    cur.execute("DELETE FROM users;")

    # Reseta autoincrement (SQLite)
    cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('users','tasks','time_entries');")

    # User seed
    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Mateus", "mateus@email.com", "hash_fake_so_pra_testar")
    )
    user_id = cur.lastrowid

    # Tasks seed
    titles = [
        "Estudar SQLite",
        "Criar endpoints da API",
        "Implementar autenticação",
        "Refatorar projeto",
        "Testar relatórios"
    ]
    task_ids = []
    for t in titles:
        cur.execute("""
            INSERT INTO tasks (user_id, title, description, status, priority)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, t, "Seed de teste", "in_progress", "medium"))
        task_ids.append(cur.lastrowid)

    # time_entries seed (últimos 5 dias)
    for task_id in task_ids:
        sessions = random.randint(1, 4)
        for _ in range(sessions):
            minutes = random.choice([15, 20, 25, 30, 45, 60])
            # cria start_time em algum dia recente
            day_offset = random.randint(0, 4)
            cur.execute("""
                INSERT INTO time_entries (task_id, start_time, end_time, duration_minutes)
                VALUES (
                    ?,
                    datetime('now', ?),
                    datetime('now', ?, ?),
                    ?
                );
            """, (
                task_id,
                f"-{day_offset} days",
                f"-{day_offset} days",
                f"+{minutes} minutes",
                minutes
            ))

    conn.commit()
    conn.close()
    print("✅ Reset + Seed concluído. Rode scripts/reports.py para ver os relatórios.")

if __name__ == "__main__":
    main()