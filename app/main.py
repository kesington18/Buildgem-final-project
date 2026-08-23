from fastapi import FastAPI

from app.db.session import Base, engine
app = FastAPI(title="Centralized Student Information System")


@app.get("/")
def root():
    return {"Hello": "World"}