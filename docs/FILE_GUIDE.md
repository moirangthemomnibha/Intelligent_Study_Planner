# What belongs in each important file?

| Location | What you write there |
|---|---|
| `backend/app/main.py` | Create FastAPI app, configure CORS/lifespan, register routers |
| `backend/app/core/config.py` | Environment-based settings and app configuration |
| `backend/app/core/security.py` | Password hashing, JWT creation and token validation |
| `backend/app/database/session.py` | Database engine and session dependency |
| `modules/<feature>/router.py` | URL endpoints for that feature |
| `modules/<feature>/schemas.py` | Input/output validation structures |
| `modules/<feature>/models.py` | Database table definitions |
| `modules/<feature>/service.py` | Actual feature logic; calculations and decisions |
| `planning/` | Priority calculation and schedule generation algorithms |
| `tracking/` | Record completed, skipped and delayed study sessions |
| `adaptation/` | Rebuild future plans after changes |
| `ai/` | Predictions, recommendations, agent tools and safety checks |
| `frontend/src/api/client.js` | All frontend-to-backend HTTP requests |
| `frontend/src/components/` | Reusable UI parts |
| `frontend/src/pages/` | Full application screens |
| `frontend/src/context/` | Shared login/profile/app state |
| `tests/` | Unit tests for algorithms and API/integration tests |

For every module, first understand the inputs and outputs, then implement the service, test it, and only then connect the router and UI.
