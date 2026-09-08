from fastapi import FastAPI

from app.db.session import Base, engine
from app.models import user
# from app.models import group, keyword, announcement
from app.api.routes import auth

app = FastAPI(title="Centralized Student Information System")
# Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"Hello": "World"}