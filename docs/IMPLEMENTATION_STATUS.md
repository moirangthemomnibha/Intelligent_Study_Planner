# Implementation Status

This file records what is actually present in the uploaded project snapshot. Update it when a feature is implemented and tested.

## Status legend
- **Implemented (baseline):** working code exists, but may not satisfy all final requirements.
- **Partial:** some required files or behavior exist; integration or important behavior is missing.
- **Placeholder:** structure/comments exist, but the feature is not functional.
- **Not present:** no implementation was found in this snapshot.

| Milestone | Main files | Status | Next action |
|---|---|---|---|
| Week 1 Part 1 foundation | `backend/app/legacy/week1_part1_foundation.py` | Implemented (baseline) | Review remaining Week 1 parts and migrate only after behavior is confirmed |
| Week 2 subjects/topics | `modules/subjects/`, `modules/topics/` | Partial | Implement CRUD services/routes and tests |
| Week 3 priority | `planning/priority.py`, `tests/test_priority.py` | Implemented (baseline) | Validate weights and add boundary/edge-case tests |
| Week 4 schedule generation | `planning/scheduler.py`, `modules/planning/` | Partial | Connect database-backed topics and remove 501 placeholder |
| Week 5 scheduling constraints | `planning/constraints.py`, `planning/scheduler.py` | Partial | Add per-day availability, topic limits, breaks and date-aware allocation |
| Week 6 session tracking | `modules/sessions/` | Partial | Add create/list/update workflows and tests |
| Week 7 adaptation | — | Not present | Design and implement deterministic rescheduling |
| Week 8 optimization | — | Not present | Add evaluation-driven optimizer and schedule quality tests |
| Week 9 persistence | `database/session.py`, SQLModel models | Partial | Define relationships, constraints, migrations and integration tests |
| Week 10 React UI | `frontend/src/` | Partial | Add forms, loading/error states and API integration |
| Week 11 AI/agent | `modules/ai/`, `modules/agent/` | Placeholder | Build deterministic recommendations first; add guarded agent actions later |
| Week 12 tests/refinement | `backend/tests/` | Partial | Expand unit, API, integration and security tests |

## Test inventory

- `test_priority.py`: checks an urgent, weak, incomplete topic scores higher than a relaxed, strong, nearly complete topic.
- `test_scheduler.py`: checks the total scheduled duration and that generated blocks have positive duration.

These two tests are not enough to establish application readiness.
