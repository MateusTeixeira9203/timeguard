from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models, schemas

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=schemas.TaskOut,
    status_code=status.HTTP_201_CREATED,
)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Cria uma nova tarefa."""
    # Regra simples: apenas garante que o usuário existe
    user = db.get(models.User, payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    task = models.Task(
        user_id=payload.user_id,
        title=payload.title,
        description=payload.description,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=List[schemas.TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    """Lista todas as tarefas."""
    tasks = db.query(models.Task).all()
    return tasks


@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Detalhe de uma tarefa."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )
    return task

