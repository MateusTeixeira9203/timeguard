from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    # Enquanto não há autenticação, o user_id vem explícito
    user_id: int


class TaskOut(TaskBase):
    id: int
    status: str
    priority: str

    class Config:
        from_attributes = True


class TimeEntryOut(BaseModel):
    id: int
    task_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None

    class Config:
        from_attributes = True


class TaskWithEntries(TaskOut):
    time_entries: List[TimeEntryOut] = []

