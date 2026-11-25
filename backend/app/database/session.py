"""Database engine, session dependency and SQLite migrations."""

from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text

from app.core.config import settings
from app.modules.planning.preferred_time_models import PreferredStudyTime
from app.modules.settings.models import UserSettings

sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False} if sqlite else {},
)


def run_sqlite_migrations():
    """Safely add missing SQLite columns without deleting existing records."""

    migrations = {
        "studysession": {
            "completed_at": "DATETIME",
            "original_planned_date": "VARCHAR",
            "rescheduled_count": "INTEGER NOT NULL DEFAULT 0",
            "missed_reason": "VARCHAR",
            "created_at": "DATETIME",
            "updated_at": "DATETIME",
        },
        "plansettings": {
            "daily_available_minutes": "INTEGER NOT NULL DEFAULT 180",
            "adaptive_scheduling": "BOOLEAN NOT NULL DEFAULT 1",
            "auto_reschedule_missed": "BOOLEAN NOT NULL DEFAULT 1",
            "auto_adjust_early_completion": "BOOLEAN NOT NULL DEFAULT 1",
            "enable_revision": "BOOLEAN NOT NULL DEFAULT 1",
            "revision_interval_days": "INTEGER NOT NULL DEFAULT 3",
            "buffer_minutes": "INTEGER NOT NULL DEFAULT 30",
        }
    }

    with engine.begin() as connection:

        for table, columns in migrations.items():

            existing_columns = connection.execute(
                text(f"PRAGMA table_info({table})")
            ).fetchall()

            existing_names = {column[1] for column in existing_columns}

            if not existing_columns:
                continue

            for column_name, column_type in columns.items():

                if column_name not in existing_names:

                    connection.execute(
                        text(
                            f"ALTER TABLE {table} "
                            f"ADD COLUMN {column_name} {column_type}"
                        )
                    )

                if column_name in ("created_at", "updated_at"):

                    connection.execute(
                        text(
                            f"UPDATE {table} "
                            f"SET {column_name} = CURRENT_TIMESTAMP "
                            f"WHERE {column_name} IS NULL"
                        )
                    )

def create_db_and_tables():
    """Create database tables and apply migrations."""

    from app.modules.students.models import Student
    from app.modules.subjects.models import Subject
    from app.modules.topics.models import Topic
    from app.modules.sessions.models import StudySession
    from app.modules.planning.models import PlanSettings
    from app.modules.auth.models import User, EmailOTP
    from app.modules.tasks.models import Task

    SQLModel.metadata.create_all(engine)

    if sqlite:
        run_sqlite_migrations()


def get_session():
    with Session(engine) as session:
        yield session