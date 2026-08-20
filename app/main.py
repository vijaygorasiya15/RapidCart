import app.models.order
import app.models.order_item
import app.models.product
import app.models.user
from app.db.database import Base, engine, get_db
from app.routers import auth, order, product, websocket
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI(title="RapidCart")

Base.metadata.create_all(bind=engine)
"""
Look at all the tables registered in Base.metadata and create them in the database if they don't already exist.
"""

app.include_router(auth.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(websocket.router)

@app.get("/")
async def test():
    return {"Message": "Just Testing it"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}