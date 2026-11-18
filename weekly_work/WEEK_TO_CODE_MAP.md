# Week-to-code map

The integrated source code belongs in `backend/` and `frontend/`. Each `weekly_work/week_XX/` folder is for milestone instructions, notes and isolated experiments; its `implementation.py` is currently a starter placeholder, not the source of truth.

| Week | Milestone | Main implementation destination |
|---|---|---|
| 1 | Project foundation + basic student data | `backend/app/modules/students/`, `backend/app/core/config.py`, `backend/app/database/`; original snapshot: `backend/app/legacy/week1_part1_foundation.py` |
| 2 | Multiple subjects, topics and exam dates | `backend/app/modules/subjects/`, `backend/app/modules/topics/` |
| 3 | Difficulty, completion and priority calculation | `backend/app/planning/priority.py`, `backend/tests/test_priority.py` |
| 4 | Generate first study plan | `backend/app/planning/scheduler.py`, `backend/app/modules/planning/` |
| 5 | Multi-day/multi-subject scheduling | `backend/app/planning/`, planning schemas and tests |
| 6 | Completed/missed study sessions | `backend/app/modules/sessions/` |
| 7 | Adaptive rescheduling | Add a dedicated adaptation service under `backend/app/` and tests |
| 8 | Improve scheduling/prioritization | `backend/app/planning/` and evaluation tests |
| 9 | Persistent database | `backend/app/database/`, SQLModel feature models and tests |
| 10 | User interface | `frontend/src/pages/`, `components/`, `api/`, `context/` |
| 11 | AI recommendations and agent groundwork | `backend/app/modules/ai/`, `backend/app/modules/agent/` |
| 12 | Testing, refinement and final integration | `backend/tests/`, `docs/` and frontend build checks |

## Current received-code note

The uploaded archive contains the original **Week 1 Part 1** implementation in `backend/app/legacy/week1_part1_foundation.py`. It includes the SQLite schema, connection, input helpers, profile/plan-settings helpers and time conversion. It does not contain the complete Weeks 1–8 combined code previously discussed. Check `docs/IMPLEMENTATION_STATUS.md` before assuming a milestone is complete.
