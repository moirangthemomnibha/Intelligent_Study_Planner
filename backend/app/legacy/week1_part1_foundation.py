#!/usr/bin/env python3
"""
Intelligent Adaptive Study Planner
Weeks 1–8
"""

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).with_name("study_planner.db")

MAX_PLAN_DAYS = 30
MAX_ASSESSMENTS = 10
REVISION_MINUTES = 30
MAX_TOPIC_HOURS_PER_DAY = 1.0
ASSESSMENT_DAILY_SHARE = 0.60
EPSILON = 0.000001


# ============================================================
# PART 1 — WEEK 1
# DATABASE CONNECTION AND INITIALISATION
# ============================================================

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialise_database():

    with connect() as db:

        db.executescript("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            completed INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL
                REFERENCES subjects(id) ON DELETE CASCADE,
            name TEXT NOT NULL COLLATE NOCASE,
            difficulty TEXT NOT NULL
                CHECK (difficulty IN ('easy', 'medium', 'hard')),
            progress INTEGER NOT NULL DEFAULT 0
                CHECK (progress BETWEEN 0 AND 100),
            estimated_hours REAL NOT NULL DEFAULT 2
                CHECK (estimated_hours > 0),
            completed INTEGER NOT NULL DEFAULT 0,
            UNIQUE(subject_id, name)
        );

        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            kind TEXT NOT NULL,
            subject_id INTEGER
                REFERENCES subjects(id) ON DELETE SET NULL,
            due_date TEXT NOT NULL,
            prep_hours REAL NOT NULL
                CHECK (prep_hours >= 0),
            completed INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS availability (
            plan_date TEXT PRIMARY KEY,
            hours REAL NOT NULL CHECK (hours >= 0),
            subject_limit INTEGER NOT NULL DEFAULT 5
                CHECK (subject_limit BETWEEN 1 AND 5)
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_date TEXT NOT NULL,
            kind TEXT NOT NULL CHECK (
                kind IN ('assessment', 'study', 'revision')
            ),
            subject_id INTEGER
                REFERENCES subjects(id) ON DELETE SET NULL,
            topic_id INTEGER
                REFERENCES topics(id) ON DELETE SET NULL,
            assessment_id INTEGER
                REFERENCES assessments(id) ON DELETE SET NULL,
            title TEXT NOT NULL,
            planned_hours REAL NOT NULL,
            actual_hours REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (
                    status IN (
                        'pending', 'completed', 'partial', 'missed'
                    )
                ),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_sessions_date
        ON sessions(plan_date);

        CREATE INDEX IF NOT EXISTS idx_sessions_topic
        ON sessions(topic_id);

        CREATE INDEX IF NOT EXISTS idx_sessions_assessment
        ON sessions(assessment_id);

        CREATE TABLE IF NOT EXISTS planner_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            plan_start TEXT NOT NULL,
            plan_days INTEGER NOT NULL
                CHECK (plan_days BETWEEN 1 AND 30)
        );
        """)

        columns = {
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(availability)"
            ).fetchall()
        }

        if "subject_limit" not in columns:
            db.execute("""
                ALTER TABLE availability
                ADD COLUMN subject_limit INTEGER NOT NULL DEFAULT 5
            """)


# ============================================================
# INPUT VALIDATION
# ============================================================

def ask_text(prompt):

    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("Please enter a value.")


def ask_int(prompt, low=0, high=None):

    while True:
        try:
            value = int(input(prompt).strip())

            if value < low:
                raise ValueError

            if high is not None and value > high:
                raise ValueError

            return value

        except ValueError:

            if high is None:
                print(f"Enter a whole number of at least {low}.")
            else:
                print(f"Enter a whole number from {low} to {high}.")


def ask_float(prompt, low=0.0, high=None):

    while True:
        try:
            value = float(input(prompt).strip())

            if value < low:
                raise ValueError

            if high is not None and value > high:
                raise ValueError

            return value

        except ValueError:

            if high is None:
                print(f"Enter a number of at least {low}.")
            else:
                print(f"Enter a number from {low} to {high}.")


def ask_yes_no(prompt):

    while True:
        answer = input(prompt).strip().lower()

        if answer in ("yes", "y"):
            return True

        if answer in ("no", "n"):
            return False

        print("Please enter yes or no.")


def ask_date(prompt, allow_today=True):

    while True:

        raw = input(prompt + " (DD-MM-YYYY): ").strip()

        try:
            parsed = datetime.strptime(
                raw, "%d-%m-%Y"
            ).date()

            if parsed < date.today():
                print("Please enter today or a future date.")
                continue

            if not allow_today and parsed == date.today():
                print("Please enter a future date.")
                continue

            return parsed.isoformat()

        except ValueError:
            print("Invalid date. Use DD-MM-YYYY.")


# ============================================================
# FLEXIBLE STUDY-TIME INPUT
# ============================================================

def ask_duration_minutes(prompt, maximum_minutes=None):

    while True:

        print(f"\n{prompt}")
        print("1. Enter hours")
        print("2. Enter minutes")
        print("3. Enter hours and minutes")

        choice = ask_int("Choose: ", 1, 3)

        if choice == 1:
            hours = ask_float("Hours: ", 0)
            minutes = round(hours * 60)

        elif choice == 2:
            minutes = ask_int("Minutes: ", 0)

        else:
            hours = ask_int("Hours: ", 0)
            extra_minutes = ask_int("Minutes (0-59): ", 0, 59)
            minutes = hours * 60 + extra_minutes

        if maximum_minutes is not None and minutes > maximum_minutes:
            print(f"Maximum allowed time is {maximum_minutes} minutes.")
            continue

        return int(minutes)


# ============================================================
# PROFILE AND PLAN SETTINGS
# ============================================================

def get_profile(db):
    return db.execute(
        "SELECT * FROM profile WHERE id = 1"
    ).fetchone()


def get_plan_settings(db):
    return db.execute(
        "SELECT * FROM planner_settings WHERE id = 1"
    ).fetchone()


def save_plan_settings(db, start, days):

    db.execute("""
        INSERT INTO planner_settings(id, plan_start, plan_days)
        VALUES(1, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            plan_start = excluded.plan_start,
            plan_days = excluded.plan_days
    """, (start.isoformat(), days))

    db.commit()


# ============================================================
# TIME CONVERSION
# ============================================================

def minutes_to_hours(minutes):
    return minutes / 60.0


def hours_to_minutes(hours):
    return round(float(hours) * 60)


def format_duration(hours):

    total_minutes = round(float(hours) * 60)
    whole_hours, remaining_minutes = divmod(total_minutes, 60)

    if whole_hours and remaining_minutes:
        return f"{whole_hours}h {remaining_minutes}m"

    if whole_hours:
        return f"{whole_hours}h"

    return f"{remaining_minutes}m"


def fmt(hours):
    return format_duration(hours)


# ==================== END OF PART 1 — WEEK 1 ====================
