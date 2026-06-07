# SafeSpace / SafeMind

SafeSpace is a demo-ready mental wellness API for private journals, mood check-ins,
supportive reflections, crisis-aware messaging, and practical resources. It is
educational software and is not a replacement for therapy or emergency care.

## Tech Stack

- Python 3.11+
- FastAPI and Pydantic
- SQLAlchemy
- SQLite by default, with PostgreSQL URL support
- JWT bearer authentication
- Optional Google OAuth and OpenAI Responses API integration

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.seed
uvicorn app.main:app --reload
```

Open `http://localhost:8000` for the demo frontend or
`http://localhost:8000/docs` for the API documentation. Demo credentials after seeding:
`demo@safespace.app` / `DemoPass123!`.

Docker is also supported:

```powershell
docker compose up --build
```

## Vercel Demo Deployment

Vercel discovers the FastAPI application through `app/index.py`. No build
command or output directory is required. Add `JWT_SECRET_KEY` in the Vercel
project settings, then deploy the repository.

For challenge demos, Vercel uses a temporary SQLite database and seeds the demo
account on function startup. Temporary data can reset between function instances.
Use a hosted PostgreSQL `DATABASE_URL` when durable production data is required.

## Environment Variables

`DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRATION_HOURS`,
`API_HOST`, and `API_PORT` configure the core app. `GOOGLE_CLIENT_ID`,
`GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` enable Google sign-in.
`OPENAI_API_KEY` and `OPENAI_MODEL` enable live AI reflections. The built-in
fallback is used when no key is present or the provider is unavailable.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/api/auth/signup` | Create account and receive JWT |
| POST | `/api/auth/login` | Log in |
| GET | `/api/auth/me` | Protected profile |
| GET/POST | `/api/journals/` | List or create journals |
| GET/PATCH/DELETE | `/api/journals/{id}` | Owned journal operations |
| GET/POST | `/api/moods/` | Mood history or check-in |
| GET | `/api/moods/summary` | Total, common mood, recent trend |
| POST | `/api/reflections/` | Reflect on an owned journal or mood |
| GET | `/api/resources/` | Categorized wellness resources |

Use `Authorization: Bearer <access_token>` for protected routes.

## Demo Flow

1. Show `/health` and interactive `/docs`.
2. Log in with the seeded demo account.
3. View seeded journals and mood history.
4. Create and update a journal.
5. Add a mood check-in and open the summary.
6. Generate a supportive reflection; point out fallback reliability.
7. Use a clearly fictional crisis phrase to show safe escalation messaging.
8. Filter the resources endpoint by category.

## Tests

```powershell
pytest
```

## Known Limitations

- JWT logout is client-side; there is no server-side token revocation list.
- SQLite schema changes use table creation rather than Alembic migrations.
- Crisis detection is intentionally simple keyword matching and can miss context.
- Resource data is static and emergency numbers are not location-specific.
- AI reflections are supportive text, not clinical advice or diagnosis.
