# Intelligent Adaptive Study Planner

A learning project for building a personalized study planner that prioritizes topics, generates study sessions, tracks progress and eventually adapts the plan when a student misses or completes sessions.

## Project layout

```text
intelligent_study_planner/
├── backend/
│   ├── app/
│   │   ├── core/          # configuration, security and shared dependencies
│   │   ├── database/      # SQLModel engine and database sessions
│   │   ├── legacy/        # preserved original implementation snapshots
│   │   ├── modules/       # feature modules: students, subjects, topics, etc.
│   │   ├── planning/      # reusable priority, scheduling and time algorithms
│   │   └── workers/       # background task entry points
│   ├── tests/             # backend unit tests
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/           # HTTP client
│       ├── components/    # reusable UI components
│       ├── context/       # shared application state
│       ├── pages/         # application screens
│       └── styles/
├── docs/                  # architecture, review, status and development guides
└── weekly_work/           # Week 1–12 plans, notes and workspaces
```

## Important project status

This archive is a **starter scaffold**, not a finished Weeks 1–12 application. The only preserved legacy milestone code is Week 1 Part 1. Several backend modules and React screens are placeholders. Read these before continuing:

1. `docs/PROJECT_CODE_REVIEW.md` — detailed review, gaps and recommendations.
2. `docs/IMPLEMENTATION_STATUS.md` — current milestone status.
3. `docs/FILE_GUIDE.md` — what belongs in each source file.
4. `weekly_work/WEEK_TO_CODE_MAP.md` — weekly milestone to source-file mapping.

## Technology

- Backend: Python, FastAPI, SQLModel, SQLite
- Frontend: React, Vite, JavaScript
- Tests: pytest

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API documentation: `http://localhost:8000/docs`

## Run the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173`.

## Run backend tests

```bash
cd backend
pytest -q
```

## Development rule

Implement business logic in backend services or reusable algorithm modules, test it, and only then connect API routes and React pages. Keep the original legacy code until each migrated behavior has been verified. Do not treat a TODO, model/schema, or static screen as a completed feature.

## Security note

Authentication and authorization are not complete in this snapshot. Do not deploy it with real student accounts or sensitive student data. Replace development secrets through environment configuration and implement ownership checks before exposing private data.
