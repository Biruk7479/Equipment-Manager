# Equipment Request Management System

Employees request workplace equipment (laptops, monitors, phones, keyboards, headsets) and managers approve or reject those requests. Approving a request deducts it from stock in the same transaction, and every status change is recorded in an append-only history.

**Stack:** Next.js (App Router) · FastAPI · PostgreSQL · SQLAlchemy · Alembic · Docker Compose

![Manager dashboard showing stock totals, request counts by status, and a requests-by-category chart](docs/screenshots/dashboard.png)

## Quick start

Requires Docker with Compose.

```bash
cp .env.example .env
# set JWT_SECRET to a long random value, e.g. the output of: openssl rand -hex 32
docker compose up --build
```

| Service | URL |
| --- | --- |
| Web app | http://localhost:3000 |
| API docs (Swagger) | http://localhost:8000/docs |

On first start the API runs migrations and seeds a manager from `MANAGER_EMAIL` / `MANAGER_PASSWORD` (default `manager@example.com` / `ChangeMe123!`). New sign-ups are employees. Managers can create more employee or manager accounts from the **Users** page.

Before deploying anywhere public:
- Change `MANAGER_PASSWORD`.
- Use a `JWT_SECRET` of at least 32 characters. The API refuses to start with a shorter one.
- Serve the app over HTTPS with `COOKIE_SECURE=true`.

## Features

| Area | Employee | Manager |
| --- | --- | --- |
| Account | Register, sign in/out, change password | Same, plus create accounts |
| Equipment | Browse, search and filter | Create and edit items and stock |
| Requests | Submit and track own requests | View all, approve or reject pending ones |
| Dashboard | Stock totals and own request counts | Stock totals and all request counts |

- Equipment lists support search by name, filtering by category and availability, and pagination.
- Request lists filter by status, employee and equipment, sort by creation date, and paginate.
- The dashboard shows totals, status counts, and a requests-by-category chart with a table view.

## Screenshots

**Reviewing a request.** The manager sees the justification, the requested quantity against current stock, and approves or rejects it. A rejection requires a comment.

![Manager reviewing a pending laptop request with the stock check and a comment box](docs/screenshots/review.png)

**Audit trail.** Every status change records who made it, when, and the manager's comment. History can't be edited or deleted.

![Approved request showing reviewer, manager comment, and the pending-to-approved history](docs/screenshots/history.png)

**All requests.** Managers filter by status, employee and equipment, sort by date, and jump straight to pending reviews.

![Manager request list with status badges, filters and review buttons](docs/screenshots/requests.png)

**Equipment.** Search by name, filter by category and availability. Only managers can add or edit items.

![Equipment inventory with categories, available quantities and an out-of-stock item](docs/screenshots/equipment.png)

**Employee view on mobile.** Employees see their own requests and counts. The layout adapts to small screens.

<p align="center">
  <img src="docs/screenshots/mobile-dashboard.png" width="280" alt="Employee dashboard on a phone">
  &nbsp;&nbsp;
  <img src="docs/screenshots/mobile-requests.png" width="280" alt="Employee's own requests on a phone">
</p>

## Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── controllers/    HTTP layer: routes, status codes, cookies
│   │   ├── services/       business rules and transaction boundaries
│   │   ├── repositories/   SQLAlchemy queries
│   │   ├── models/         ORM entities
│   │   ├── schemas/        Pydantic request/response models
│   │   ├── core/           settings, security (JWT, hashing), error handling
│   │   ├── db/             engine, session, declarative base
│   │   ├── dependencies.py auth and role dependencies
│   │   ├── router.py       mounts controllers under /api/v1
│   │   ├── seed.py         first manager account
│   │   └── main.py
│   ├── alembic/            migrations
│   └── tests/              API tests against PostgreSQL
├── frontend/
│   └── src/
│       ├── app/            routes: (auth) pages and the signed-in (app) area
│       ├── features/       auth, equipment, requests, users, dashboard
│       ├── components/     shared UI and layout
│       ├── lib/            API client, types, formatting, helpers
│       └── proxy.ts        redirects signed-out visitors to /login
└── docker-compose.yml
```

A request flows **controller → service → repository → model**. Controllers never touch the database directly, and repositories never make business decisions.

## How the key rules are enforced

**Authentication.** Login issues a short-lived access token (15 min) and a refresh token (7 days), both JWTs in `httpOnly`, `SameSite=Lax` cookies. Refresh tokens are stored server-side and rotated on every use, so logout and password changes revoke sessions immediately. Changing your password signs out all your other sessions. The frontend refreshes transparently when a request returns 401.

**Authorization** is checked on the server for every endpoint:
- Only managers can create or edit equipment, review requests, or manage users.
- Only employees can submit requests.
- Employees only ever see their own requests. Another user's request returns `404`, so IDs can't be probed.
- Request bodies reject unknown fields (`extra="forbid"`), so protected fields such as `status`, `requester_id` or `reviewer_id` cannot be supplied.

**Approval is atomic.** Approving locks the request and the equipment row (`SELECT … FOR UPDATE`), checks stock, decrements it, updates the request and writes history in a single transaction. If any step fails, nothing is saved. A database `CHECK` constraint also keeps `available_quantity` from going negative.

**Status transitions.** Only `pending → approved` and `pending → rejected` are allowed. Reviewing an already reviewed request returns `409 invalid_status_transition`. A rejection requires a non-blank comment.

**History is immutable.** Every change, including the initial submission, stores the previous status, new status, actor, timestamp and comment. The API has no update or delete endpoint for history, and a PostgreSQL trigger rejects any `UPDATE` or `DELETE` on the table.

**Validation.** Quantities must be positive, and stock can't be negative. Equipment names are unique case-insensitively, emails are unique, and an employee can't have two pending requests for the same item.

## API

All endpoints live under `/api/v1`. Interactive docs are at `/docs`.

| Method | Path | Access |
| --- | --- | --- |
| POST | `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout` | Public |
| GET | `/auth/me` | Signed in |
| POST | `/auth/change-password` | Signed in |
| GET / POST | `/users` | Manager |
| GET | `/equipment`, `/equipment/{id}` | Signed in |
| POST / PUT | `/equipment`, `/equipment/{id}` | Manager |
| GET | `/requests`, `/requests/{id}`, `/requests/{id}/history` | Own requests, or all for managers |
| POST | `/requests` | Employee |
| POST | `/requests/{id}/approve`, `/requests/{id}/reject` | Manager |
| GET | `/dashboard` | Signed in (request counts scoped to the caller) |

List endpoints accept `page` and `page_size` (max 100) and return `{ items, total, page, page_size }`.

Errors always use the same shape:

```json
{
  "error": {
    "code": "insufficient_stock",
    "message": "Insufficient stock: 2 available, 5 requested",
    "details": null
  }
}
```

Validation errors use `422` with `details: [{ "field": "quantity", "message": "..." }]`. Other codes: `401` (not signed in), `403` (wrong role), `404` (not found or not yours), `409` (duplicate, stock, or invalid transition).

## Local development

**Backend** (Python 3.12, [uv](https://docs.astral.sh/uv/), a PostgreSQL instance):

```bash
cd backend
cp .env.example .env          # point DATABASE_URL at your database
uv sync
uv run alembic upgrade head
uv run python -m app.seed
uv run uvicorn app.main:app --reload
```

**Frontend** (Node 22):

```bash
cd frontend
npm install
npm run dev                   # proxies /api to API_URL (default http://localhost:8000)
```

**Tests** run against a real PostgreSQL database. The suite drops and recreates the schema, so point it at a throwaway database:

```bash
cd backend
TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/equipment_test uv run pytest
```

**Lint:** `uv run ruff check .` in `backend/`, `npm run lint` in `frontend/`.

## Git workflow

Each feature was built on its own branch (`feat/…`, `fix/…`, `chore/…`) with [Conventional Commits](https://www.conventionalcommits.org/) and merged into `main` with `--no-ff`, so every feature stays visible in the history.
