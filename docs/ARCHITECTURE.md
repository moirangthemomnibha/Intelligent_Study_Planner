# Architecture

```text
React + Vite frontend
  components / pages / contexts / api client
                |
                | HTTP JSON (/api/v1)
                v
FastAPI backend
  routers -> services -> repositories/database
                |
       planning + tracking + adaptation
                |
       AI analysis / recommendation / agent
```

## Backend module convention
Each feature module can contain:
- `router.py`: HTTP endpoints only; validate input and call service functions.
- `schemas.py`: Pydantic request/response objects.
- `models.py`: SQLModel database tables (when persistence is introduced).
- `service.py`: business rules and orchestration.

Keep scheduling logic independent of FastAPI so it can be tested directly.
