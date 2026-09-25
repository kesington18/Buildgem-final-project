from fastapi import FastAPI

# from app.db.session import Base, engine
from app.models import user, group, keyword, announcement
from app.api.routes import webhook, auth, keywords, admin_groups, admin_announcements, admin_analytics

app = FastAPI(title="Centralized Student Information System")
# Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"Hello": "World"}

app.include_router(webhook.telegram_router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(keywords.router, prefix="/api/v1")
app.include_router(admin_groups.router, prefix="/api/v1")
app.include_router(admin_announcements.router, prefix="/api/v1")
app.include_router(admin_analytics.router, prefix="/api/v1")