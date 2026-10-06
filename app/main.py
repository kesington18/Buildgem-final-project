from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401  (registers all models with SQLAlchemy)
from app.config import settings
from app.api.routes import (
    webhook, auth, keywords, admin_groups,
    admin_announcements, admin_analytics,
    groups, announcements, notification,
)

app = FastAPI(title="Centralized Student Information System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,  # JWT travels in the Authorization header, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(webhook.telegram_router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(keywords.router)
app.include_router(admin_groups.router, prefix="/api/v1")
app.include_router(admin_announcements.router, prefix="/api/v1")
app.include_router(admin_analytics.router, prefix="/api/v1")
app.include_router(groups.router)
app.include_router(announcements.router)
app.include_router(notification.router)
