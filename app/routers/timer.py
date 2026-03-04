from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app import models, schemas
from app.services import timer_service

router = APIRouter(prefix="/timer", tags=["timer"])


@router.post("/start/{task_id}", response_model=schemas.TimeEntryOut)
def start_timer(task_id: int, db: Session = Depends(get_db)):
    """Inicia um timer para uma tarefa."""
    entry = timer_service.start_timer(db, task_id)
    return entry


@router.post("/stop/{task_id}", response_model=schemas.TimeEntryOut)
def stop_timer(task_id: int, db: Session = Depends(get_db)):
    """Encerra o timer aberto mais recente de uma tarefa."""
    entry = timer_service.stop_timer(db, task_id)
    return entry


@router.get("/entries/{task_id}", response_model=List[schemas.TimeEntryOut])
def list_entries(task_id: int, db: Session = Depends(get_db)):
    """Lista registros de tempo de uma tarefa."""
    stmt = (
        select(models.TimeEntry)
        .where(models.TimeEntry.task_id == task_id)
        .order_by(models.TimeEntry.start_time.desc())
    )
    entries = db.scalars(stmt).all()
    return list(entries)

