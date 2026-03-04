from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app import models


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def start_timer(db: Session, task_id: int) -> models.TimeEntry:
    """Inicia um timer para a tarefa, garantindo apenas uma sessão aberta."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )

    # Regra: apenas uma sessão aberta por tarefa
    open_entry = db.scalar(
        select(models.TimeEntry).where(
            models.TimeEntry.task_id == task_id,
            models.TimeEntry.end_time.is_(None),
        )
    )
    if open_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um timer em execução para esta tarefa",
        )

    entry = models.TimeEntry(
        task_id=task_id,
        start_time=_utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def stop_timer(db: Session, task_id: int) -> models.TimeEntry:
    """Encerra o timer aberto mais recente de uma tarefa e calcula a duração."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )

    stmt = (
        select(models.TimeEntry)
        .where(
            models.TimeEntry.task_id == task_id,
            models.TimeEntry.end_time.is_(None),
        )
        .order_by(desc(models.TimeEntry.start_time))
        .limit(1)
    )
    entry: Optional[models.TimeEntry] = db.scalar(stmt)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não há timer em execução para esta tarefa",
        )

    now = _utcnow()
    entry.end_time = now
    # Cálculo em Python (portável)
    duration_minutes = int((entry.end_time - entry.start_time).total_seconds() / 60)
    entry.duration_minutes = max(duration_minutes, 0)

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

