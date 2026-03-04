import sqlite3
from pathlib import Path

DB_PATH = Path("timeguard.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def start_timer(conn: sqlite3.Connection, task_id: int) -> int:
    # Verifica se já existe sessão aberta pra essa tarefa
    open_entry = conn.execute(
        "SELECT id FROM time_entries WHERE task_id = ? AND end_time IS NULL LIMIT 1",
        (task_id,)
    ).fetchone()

    if open_entry:
        raise ValueError(f"Já existe timer aberto para task_id={task_id} (time_entry_id={open_entry['id']}).")

    cur = conn.execute(
        "INSERT INTO time_entries (task_id, start_time) VALUES (?, datetime('now'))",
        (task_id,)
    )
    conn.commit()
    return cur.lastrowid

def stop_timer(conn: sqlite3.Connection, task_id: int) -> int:
    # Pega a sessão aberta mais recente
    entry = conn.execute(
        """
        SELECT id, start_time
        FROM time_entries
        WHERE task_id = ? AND end_time IS NULL
        ORDER BY id DESC
        LIMIT 1
        """,
        (task_id,)
    ).fetchone()

    if not entry:
        raise ValueError(f"Não existe timer aberto para task_id={task_id}.")

    # Calcula duração em minutos usando datetime do SQLite
    conn.execute(
        """
        UPDATE time_entries
        SET
          end_time = datetime('now'),
          duration_minutes = CAST((julianday(datetime('now')) - julianday(start_time)) * 24 * 60 AS INTEGER)
        WHERE id = ?
        """,
        (entry["id"],)
    )
    conn.commit()
    return entry["id"]

def show_task_entries(conn: sqlite3.Connection, task_id: int):
    rows = conn.execute(
        """
        SELECT id, task_id, start_time, end_time, duration_minutes
        FROM time_entries
        WHERE task_id = ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (task_id,)
    ).fetchall()

    print(f"\n📌 Últimos time_entries da task_id={task_id}:")
    for r in rows:
        print(dict(r))

def main():
    conn = get_conn()
    try:
        # Pegando uma task existente (a última criada)
        task = conn.execute("SELECT id, title FROM tasks ORDER BY id DESC LIMIT 1").fetchone()
        if not task:
            print("❌ Nenhuma task encontrada. Rode scripts/test_db.py primeiro.")
            return

        task_id = task["id"]
        print(f"🎯 Usando task_id={task_id} ({task['title']})")

        # START
        te_id = start_timer(conn, task_id)
        print(f"✅ START: time_entry_id={te_id}")

        # (Dica: pra testar duração real, espera 1-2 minutos e roda STOP depois)
        input("⏳ Aperte ENTER para dar STOP (espera uns segundos/minutos se quiser)... ")

        # STOP
        closed_id = stop_timer(conn, task_id)
        print(f"✅ STOP: time_entry_id={closed_id}")

        show_task_entries(conn, task_id)

    finally:
        conn.close()

if __name__ == "__main__":
    main()