import sqlite3
from pathlib import Path

DB_PATH = Path("timeguard.db")

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON;")
    return c

def total_time_per_task(user_id: int):
    with conn() as db:
        rows = db.execute("""
            SELECT
              t.id AS task_id,
              t.title,
              t.status,
              COALESCE(SUM(te.duration_minutes), 0) AS total_minutes,
              COUNT(te.id) AS sessions
            FROM tasks t
            LEFT JOIN time_entries te
              ON te.task_id = t.id AND te.duration_minutes IS NOT NULL
            WHERE t.user_id = ?
            GROUP BY t.id
            ORDER BY total_minutes DESC, t.id DESC;
        """, (user_id,)).fetchall()

    print("\n⏱️ Tempo total por tarefa:")
    for r in rows:
        print(dict(r))

def total_time_per_day(user_id: int, days: int = 7):
    with conn() as db:
        rows = db.execute("""
            SELECT
              date(te.start_time) AS day,
              COALESCE(SUM(te.duration_minutes), 0) AS total_minutes,
              COUNT(te.id) AS sessions
            FROM time_entries te
            JOIN tasks t ON t.id = te.task_id
            WHERE t.user_id = ?
              AND te.duration_minutes IS NOT NULL
              AND te.start_time >= datetime('now', ?)
            GROUP BY date(te.start_time)
            ORDER BY day DESC;
        """, (user_id, f"-{days} days")).fetchall()

    print(f"\n📅 Tempo total por dia (últimos {days} dias):")
    for r in rows:
        print(dict(r))

def top_tasks(user_id: int, limit: int = 5):
    with conn() as db:
        rows = db.execute("""
            SELECT
              t.id AS task_id,
              t.title,
              COALESCE(SUM(te.duration_minutes), 0) AS total_minutes
            FROM tasks t
            LEFT JOIN time_entries te
              ON te.task_id = t.id AND te.duration_minutes IS NOT NULL
            WHERE t.user_id = ?
            GROUP BY t.id
            ORDER BY total_minutes DESC
            LIMIT ?;
        """, (user_id, limit)).fetchall()

    print(f"\n🏆 Top {limit} tarefas por tempo:")
    for r in rows:
        print(dict(r))

def tasks_without_time(user_id: int):
    with conn() as db:
        rows = db.execute("""
            SELECT t.id AS task_id, t.title, t.status
            FROM tasks t
            LEFT JOIN time_entries te ON te.task_id = t.id
            WHERE t.user_id = ?
            GROUP BY t.id
            HAVING COUNT(te.id) = 0
            ORDER BY t.id DESC;
        """, (user_id,)).fetchall()

    print("\n🧊 Tarefas sem tempo registrado:")
    for r in rows:
        print(dict(r))

def main():
    user_id = 1  # por enquanto fixo; depois a API pega do usuário logado
    total_time_per_task(user_id)
    total_time_per_day(user_id, days=7)
    top_tasks(user_id, limit=5)
    tasks_without_time(user_id)

if __name__ == "__main__":
    main()