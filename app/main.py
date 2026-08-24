from fastapi import FastAPI

from app.db.session import Base, engine
from app.models import user, group, keyword, announcement
app = FastAPI(title="Centralized Student Information System")
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"Hello": "World"}