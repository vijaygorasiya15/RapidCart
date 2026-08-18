from app.db.database import get_db
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI(title="RapidCart")

@app.get("/")
async def test():
    return {"Message": "Just Testing it"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}