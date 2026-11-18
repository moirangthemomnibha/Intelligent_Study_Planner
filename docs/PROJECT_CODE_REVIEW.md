# Project Code Review and Organization Guide

**Reviewed source:** uploaded `intelligent_study_planner(1).zip`  
**Review scope:** source files present in that archive only.  
**Review outcome:** this archive is a modular starter scaffold with one retained legacy Week 1 Part 1 source file. It is not yet the complete Weeks 1–12 application.

## 1. What is in this project?

The project is arranged as a full-stack application:

- `backend/` — Python + FastAPI API, SQLModel database layer, planning algorithms and tests.
- `frontend/` — React + Vite user interface.
- `docs/` — project explanation, architecture, development and testing guidance.
- `weekly_work/` — week-by-week roadmap and workspaces.

The folder layout is sensible for a modular full-stack project. However, several modules are intentionally placeholders, and the weekly `implementation.py` files contain only TODO comments. The real implementation should live in the backend/frontend feature folders, not be duplicated in those weekly workspaces.

## 2. Existing implementation, by area

### Backend foundation

| File/folder | Current responsibility | Current state |
|---|---|---|
| `backend/app/main.py` | Creates FastAPI app, CORS, startup DB creation, router registration | Basic app entry point exists |
| `backend/app/core/config.py` | Environment settings | Basic settings exist; default JWT secret is a development placeholder |
| `backend/app/core/security.py` | Password/JWT security | TODO only; authentication is not implemented |
| `backend/app/database/session.py` | SQLModel engine and session dependency | Basic engine/session setup exists |
| `backend/app/modules/students/` | Student profile model, schema, create/read service and route | Partial; create endpoint exists, ownership/authentication absent |
| `backend/app/modules/subjects/` | Subject model/schema/service/router | Model/schema exist; service/router are placeholders |
| `backend/app/modules/topics/` | Topic model/schema/service/router | Model/schema exist; service/router are placeholders |
| `backend/app/modules/planning/` | Plan settings and planning request/response structures | Partial; settings persistence exists, generation endpoint returns HTTP 501 |
| `backend/app/planning/priority.py` | Rule-based priority score | Implemented baseline function |
| `backend/app/planning/scheduler.py` | Greedy multi-day schedule generator | Implemented baseline; does not yet enforce all planner constraints |
| `backend/app/planning/constraints.py` | Session duration checks and shared constants | Basic validation only |
| `backend/app/planning/time_utils.py` | Hour/minute conversion and display formatting | Basic utilities exist |
| `backend/app/modules/sessions/` | Study-session tracking | Model/schema exist; route/service are placeholders |
| `backend/app/modules/ai/` | Recommendation API groundwork | Static placeholder recommendation only; no model/AI integration |
| `backend/app/modules/agent/` | Agent orchestration groundwork | Allowed-tool list and design notes only |
| `backend/app/modules/auth/` | Authentication feature | Placeholder files; not functional |
| `analytics/`, `reminders/`, `reports/`, `health/` | Supporting feature modules | Health check exists; others are mostly placeholders |
| `backend/app/workers/` | Background jobs | Placeholder worker files |
| `backend/app/legacy/week1_part1_foundation.py` | Original SQLite Week 1 Part 1 foundation | Substantial source snapshot retained; see Week 1 section below |

### Frontend

| File/folder | Current responsibility | Current state |
|---|---|---|
| `frontend/src/App.jsx` | Basic page switching | Basic shell with Dashboard, Subjects, Planner and Agent views |
| `frontend/src/api/client.js` | HTTP requests to backend | Student creation and plan generation calls; other methods missing |
| `frontend/src/context/AuthContext.jsx` | Login state | In-memory placeholder only; no signup/signin/logout |
| `frontend/src/context/PlannerContext.jsx` | Shared subjects and plan state | Basic in-memory state only |
| `frontend/src/pages/` | Dashboard, Subjects, Planner screens | Static starter screens; forms and API integration missing |
| `frontend/src/components/` | Reusable UI components | Small starter components exist |

**Important:** the uploaded project uses React + Vite. It does not contain the previously discussed Streamlit frontend implementation.

## 3. Week-by-week implementation status

| Week | Intended milestone | Evidence in this archive | Status |
|---|---|---|---|
| 1 | Foundation and student data | `legacy/week1_part1_foundation.py` contains SQLite schema, connection, input validation, duration helpers, profile/settings access and time conversion | Part 1 source exists; not the full Week 1 feature |
| 2 | Subjects, topics and exam dates | SQLModel models and Pydantic schemas exist | Partial; CRUD services/routes absent |
| 3 | Difficulty, completion and priority | `planning/priority.py` and one priority test | Baseline implemented |
| 4 | First study plan | `planning/scheduler.py`, planning service/schema | Partial; API route deliberately returns 501 and does not load database topics |
| 5 | Multi-day/multi-subject scheduling | Greedy scheduler and basic constraints | Basic baseline only; no robust allocation, calendar or full constraint handling |
| 6 | Completed/missed session tracking | Session model and update schema | Partial; no session CRUD/workflow |
| 7 | Adaptive rescheduling | No adaptation service or workflow found | Not implemented in this archive |
| 8 | Improved scheduling/prioritization | No optimizer/evaluation implementation found | Not implemented in this archive |
| 9 | Persistent database | SQLModel engine, models and table creation | Foundation exists; feature coverage and migration strategy incomplete |
| 10 | User interface | React/Vite starter pages and API client | UI shell exists; major forms and integration incomplete |
| 11 | AI recommendations/agent | Static recommendation stub and agent design placeholder | Groundwork only; not a functioning AI feature |
| 12 | Testing/refinement | Two small tests: priority and scheduler | Minimal tests only; not a complete test suite |

## 4. Important issues found

1. **The archive does not contain the full Week 1–8 combined application code.** The only legacy source file is explicitly named `week1_part1_foundation.py` and ends after Part 1.
2. **All 12 weekly `implementation.py` files are templates.** They contain TODO comments, not the actual implementation for their respective weeks.
3. **Several module files had an accidental literal `\\n` at the end**, which caused Python syntax errors. Those stray characters have been removed in this organized copy; the modules remain placeholders, not implemented features.
4. **The planning API is not connected.** `POST /api/v1/planning/generate` currently returns HTTP 501.
5. **Subject/topic/session endpoints are missing.** Their routers contain TODOs.
6. **Authentication is not implemented.** The frontend auth context is local state only, and backend security helpers are TODOs. Do not use this as a multi-user production app yet.
7. **Student ownership is not enforced.** Several schemas accept `student_id` from the request, but there is no authenticated-user authorization layer.
8. **Two database approaches coexist.** The legacy Week 1 file uses `sqlite3` and a database beside that file; the modular backend uses SQLModel and `settings.database_url`. They are not yet integrated and do not automatically share data.
9. **The baseline scheduler has limitations.** It processes topics in input order; the service sorts by priority, but the scheduler does not itself enforce topic-specific daily caps, availability by date, breaks, assessment deadlines, revision spacing or missed-session recovery.
10. **Tests are too small for the stated project scope.** Add validation, persistence, API, session tracking, adaptation, authentication and frontend integration tests before calling the app complete.
11. **The archive includes `frontend/node_modules`, Python bytecode/cache files, OS metadata and a local database.** These are generated/local artifacts, not source code. The cleaned archive omits them; install dependencies locally and create a fresh database when needed.

## 5. Recommended source-of-truth locations

Use these destinations to avoid duplicated code:

- Student profile: `backend/app/modules/students/`
- Subjects: `backend/app/modules/subjects/`
- Topics: `backend/app/modules/topics/`
- Priority and scheduling algorithms: `backend/app/planning/`
- Plan API/settings: `backend/app/modules/planning/`
- Session tracking: `backend/app/modules/sessions/`
- Authentication: `backend/app/modules/auth/` and `backend/app/core/security.py`
- AI recommendations: `backend/app/modules/ai/`
- Agent tools/orchestration: `backend/app/modules/agent/`
- React screens: `frontend/src/pages/`
- Reusable UI: `frontend/src/components/`
- HTTP integration: `frontend/src/api/client.js`
- Shared client state: `frontend/src/context/`
- Tests: `backend/tests/`
- Weekly notes and progress: `weekly_work/week_XX/`

Keep `backend/app/legacy/week1_part1_foundation.py` as the preserved original until its functions are migrated and tested. Do not delete it just because the modular equivalent is being developed.

## 6. Recommended implementation order

1. Confirm and preserve the complete original Week 1–8 code (if it exists outside this archive); do not recreate missing functions by guessing.
2. Decide on one database source of truth. Recommended target for this scaffold: SQLModel through `backend/app/database/session.py`; migrate legacy SQLite behavior carefully and test the migration.
3. Complete student profile CRUD and add authentication/ownership before exposing private student data.
4. Complete subject and topic CRUD, validation and tests.
5. Expand priority calculation and scheduler with explicit inputs for dates, daily availability and constraints.
6. Connect the planning endpoint to database-backed services and persist generated sessions.
7. Implement completed/missed/partial session workflows and deterministic adaptive rescheduling.
8. Connect React forms/pages to real API methods.
9. Add analytics/recommendations only after reliable progress/session history exists.
10. Expand automated tests and document how to run the complete application.

## 7. Verification

The organized copy was checked for Python syntax after removing the accidental literal suffixes from placeholder files. This is a syntax check, not proof that the whole application runs correctly. Runtime tests still depend on installing the packages in `backend/requirements.txt` and resolving the functional gaps listed above.
