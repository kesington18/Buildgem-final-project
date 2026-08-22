# Centralized Student Information System (Telegram)

A backend system that monitors an authorized Telegram group via webhook, detects keyword-matched announcements (exams, deadlines, venue changes, etc.), and surfaces them to students through a centralized platform with search, filtering, and notifications.

Full requirements live in the project PRD (see `/docs` or the shared drive — ask in the team channel if you don't have it).

---

## Tech Stack

| Layer                     | Technology                                          |
|---                        |                                                  ---|
| Backend API               | Python / FastAPI                                    |
| Telegram Integration      | python-telegram-bot (or aiogram) — webhook mode     |
| Database                  | PostgreSQL (hosted on [Pxxl.app](https://pxxl.app)) |
| ORM                       | SQLAlchemy (Alembic for migrations)                 |
| Caching/Background Tasks  | Redis (hosted on [Upstash](https://upstash.com))    |
| Authentication            | JWT                                                 |
| Deployment                | Docker                                              |

---

## Project Structure

```
app/
├── main.py                # FastAPI app entrypoint
├── config.py              # Settings (env vars, DB/Redis URLs)
├── api/
│   ├── deps.py             # Shared dependencies (auth, db session)
│   └── routes/
│       ├── webhook.py        # POST /webhook/telegram
│       ├── announcements.py  # GET/search/filter announcements
│       ├── keywords.py       # Admin: manage keywords
│       ├── groups.py         # Admin: manage authorized groups
│       └── auth.py           # Student/admin login, JWT issuance
├── core/
│   ├── security.py         # JWT + Telegram secret-token verification
│   ├── notifications.py    # Notification dispatch logic
│   └── redis_client.py     # Redis connection
├── models/                # SQLAlchemy models
│   ├── announcement.py
│   ├── keyword.py
│   ├── group.py
│   └── user.py
├── schemas/                # Pydantic request/response schemas
├── services/
│   ├── telegram_client.py   # setWebhook, sendMessage helpers
│   ├── keyword_matcher.py   # Keyword detection logic
│   └── background_tasks.py  # Async processing after webhook receipt
└── db/
    ├── session.py
    └── migrations/          # Alembic

frontend/     # Student web app
tests/
docker-compose.yml
Dockerfile
requirements.txt
.env.example
```

---

## Team & Task Split

Three tracks, each owning a full vertical slice (models → endpoints → tests). See `TASK_BREAKDOWN.md` for full details.

| Track                                | Owner      | Scope                                                  |
|---                                   |---         |                                                     ---|
| **Telegram Integration & Ingestion** | Engineer 1 | Webhook, keyword matcher, background task pipeline     |
| **Auth & Admin Management**          | Engineer 2 | JWT auth, keyword/group/announcement admin, analytics  |
| **Student Platform & Notifications** | Engineer 3 | Announcement search/filter, notifications, preferences |

---

## Getting Started (all teammates)

### 1. Clone the repo
```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. Create your local `.env`
Copy the example file and fill in the real values (shared privately in the team chat — **never commit real credentials**):
```bash
cp .env.example .env
```

You'll need:
- `DATABASE_URL` — shared Pxxl Postgres connection string
- `REDIS_URL` — shared Upstash Redis connection string

### 3. Install dependencies locally (for your editor/IDE support)
```bash
pip install -r requirements.txt
```

### 4. Build and run with Docker
```bash
docker compose up --build
```
This builds the app image and starts it on `http://localhost:8000`.

### 5. Verify it's working
Visit `http://localhost:8000/docs` — you should see FastAPI's auto-generated Swagger UI.

---

## Database

- **Shared PostgreSQL instance** hosted on Pxxl — one schema, used by everyone. This is *not* a local per-person database; test data you add is visible to the whole team.
- Schema is currently built via SQLAlchemy's `Base.metadata.create_all()` during early development. The team is moving to **Alembic** migrations once the schema stabilizes — see `MIGRATIONS.md` (or ask in the team channel) before making schema changes at that point.
- **Do not** manually edit tables via pgAdmin once Alembic is in use — all schema changes should go through migrations so everyone stays in sync.

## Redis

- Shared instance hosted on Upstash (free tier). Used for background task support and will back the notification dispatch pipeline.

---

## Environment Variables

See `.env.example` for the full list of required variables. Never commit a real `.env` file — it's already in `.gitignore`.

---

## Contributing Workflow

1. Pull latest `main`/`master` before starting new work.
2. Work in your own track's files where possible to minimize merge conflicts.
3. Coordinate in the team channel before running schema-changing commands (Alembic migrations) against the shared database.
4. Open a PR for review before merging — cross-track review is encouraged, since that's where interface mismatches between tracks tend to surface.

---

## Useful Commands

```bash
# Start everything
docker compose up --build

# Stop everything
docker compose down

# Run tests
docker compose exec app pytest

# Open a shell inside the running app container
docker compose exec app bash
```
