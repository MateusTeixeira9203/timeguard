import sqlite3
from pathlib import Path

DB_PATH = Path("timeguard.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # MUITO IMPORTANTE no SQLite: FK por conexão
    conn.execute("PRAGMA foreign_keys = ON;")

    cur = conn.cursor()

    # 1) Criar um usuário
    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Mateus", "mateus@email.com", "hash_fake_so_pra_testar")
    )
    user_id = cur.lastrowid
    print(f"✅ user_id criado: {user_id}")

    # 2) Criar uma tarefa desse usuário
    cur.execute(
        """
        INSERT INTO tasks (user_id, title, description, status, priority)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, "Estudar SQLite", "Aprender PK/FK e JOIN", "in_progress", "high")
    )
    task_id = cur.lastrowid
    print(f"✅ task_id criado: {task_id}")

    # 3) Criar um registro de tempo (uma sessão)
    cur.execute(
        """
        INSERT INTO time_entries (task_id, start_time, end_time, duration_minutes)
        VALUES (?, datetime('now'), datetime('now'), ?)
        """,
        (task_id, 25)
    )
    time_entry_id = cur.lastrowid
    print(f"✅ time_entry_id criado: {time_entry_id}")

    conn.commit()

    # 4) Ver tudo junto com JOIN
    rows = cur.execute(
        """
        SELECT
          u.id AS user_id,
          u.name AS user_name,
          t.id AS task_id,
          t.title AS task_title,
          t.status,
          te.id AS time_entry_id,
          te.duration_minutes
        FROM users u
        JOIN tasks t ON t.user_id = u.id
        JOIN time_entries te ON te.task_id = t.id
        ORDER BY te.id DESC
        LIMIT 5;
        """
    ).fetchall()

    print("\n📌 Últimos registros (JOIN):")
    for r in rows:
        print(dict(r))

    conn.close()

if __name__ == "__main__":
    main()