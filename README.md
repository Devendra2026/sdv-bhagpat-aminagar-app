# Baghpat Backend

FastAPI backend for the Baghpat website forms.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Set your Postgres connection string in `.env`:

```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
FRONTEND_ORIGIN=http://localhost:3000
CLERK_WEBHOOK_SECRET=whsec_your_clerk_webhook_secret
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Routes

Contact:

```text
POST   /api/contact
GET    /api/contact
GET    /api/contact/{id}
PUT    /api/contact/{id}
DELETE /api/contact/{id}
```

Grievance:

```text
POST   /api/grievance
GET    /api/grievance
GET    /api/grievance/{id}
PUT    /api/grievance/{id}
DELETE /api/grievance/{id}
```

Clerk webhook:

```text
POST /api/clerk/webhook
```

Use this URL in Clerk Dashboard webhook settings. The handler currently stores only `user.created` events into the `users` table. New users get `role="user"` by default.
