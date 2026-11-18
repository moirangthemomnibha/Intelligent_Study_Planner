from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import create_db_and_tables

# Import application routers
from app.modules.students.router import router as students_router
from app.modules.subjects.router import router as subjects_router
from app.modules.topics.router import router as topics_router
from app.modules.planning.router import router as planning_router
from app.modules.sessions.router import router as sessions_router
from app.modules.ai.router import router as ai_router
from app.modules.agent.router import router as agent_router
from app.modules.auth.router import router as auth_router

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Register API routers
routers = [
    students_router,
    subjects_router,
    topics_router,
    planning_router,
    sessions_router,
    ai_router,
    agent_router,
    auth_router,
]

for feature_router in routers:
    app.include_router(
        feature_router,
        prefix="/api/v1",
    )


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Intelligent Adaptive Study Planner API is running."
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }