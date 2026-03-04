from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.routers import tasks, timer


app = FastAPI(title="TimeGuard")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health-db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}


app.include_router(tasks.router)
app.include_router(timer.router)
