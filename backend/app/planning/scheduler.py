"""
Intelligent Adaptive Multi-Day Study Scheduler.
Supports preferred study days and time slots.
"""

from datetime import date, datetime, timedelta
from math import ceil

MAX_SESSION_MINUTES = 90


def convert_time_to_minutes(value) -> int:
    """Convert a time object or HH:MM string into minutes."""

    if hasattr(value, "hour") and hasattr(value, "minute"):
        return value.hour * 60 + value.minute

    parsed_time = datetime.strptime(str(value), "%H:%M")
    return parsed_time.hour * 60 + parsed_time.minute


def build_schedule(
    topics: list[dict],
    available_minutes: int,
    days: int,
    start_date: date | None = None,
    preferred_times: list | None = None
) -> list[dict]:

    if available_minutes <= 0:
        raise ValueError("Available minutes must be greater than zero.")

    if days <= 0:
        raise ValueError("Planning days must be greater than zero.")

    if start_date is None:
        start_date = date.today()

    plan = []

    # ------------------------------------------
    # PREPARE PREFERRED STUDY DAYS
    # ------------------------------------------

    preferred_daily_minutes = {}

    if preferred_times:
        for item in preferred_times:

            day = int(item.day_of_week)

            start_minutes = convert_time_to_minutes(
                item.start_time
            )

            end_minutes = convert_time_to_minutes(
                item.end_time
            )

            duration = end_minutes - start_minutes

            if duration <= 0:
                continue

            preferred_daily_minutes[day] = (
                preferred_daily_minutes.get(day, 0)
                + duration
            )

    # ------------------------------------------
    # PREPARE TOPICS
    # ------------------------------------------

    prepared_topics = []

    for topic in topics:

        completion = max(
            0,
            min(100, float(topic.get("completion_percent", 0)))
        )

        if completion >= 100:
            continue

        estimated = int(topic.get("estimated_minutes", 0))

        if estimated <= 0:
            continue

        learning_speed = max(
            0.1,
            float(topic.get("learning_speed", 1.0))
        )

        remaining = ceil(
            estimated
            * (100 - completion) / 100
            * learning_speed
        )

        prepared_topics.append({
            **topic,
            "remaining_minutes": remaining
        })

    prepared_topics.sort(
        key=lambda topic: float(
            topic.get(
                "priority_score",
                topic.get("priority", 0)
            )
        ),
        reverse=True
    )

    # ------------------------------------------
    # TRACK DAILY WORKLOAD
    # ------------------------------------------

    daily_usage = [0] * days

    # ------------------------------------------
    # GENERATE STUDY SCHEDULE
    # ------------------------------------------

    for topic in prepared_topics:

        minutes_left = topic["remaining_minutes"]

        for day_index in range(days):

            if minutes_left <= 0:
                break

            current_date = start_date + timedelta(
                days=day_index
            )

            weekday = current_date.weekday()

            if preferred_times:
                daily_limit = min(
                    available_minutes,
                    preferred_daily_minutes.get(weekday, 0)
                )
            else:
                daily_limit = available_minutes

            remaining_daily = (
                daily_limit - daily_usage[day_index]
            )

            if remaining_daily <= 0:
                continue

            chunk = min(
                minutes_left,
                remaining_daily,
                MAX_SESSION_MINUTES
            )

            plan.append({
                "topic_id": topic.get("id"),
                "topic_name": topic.get(
                    "name",
                    "Untitled topic"
                ),
                "day": current_date.isoformat(),
                "duration_minutes": chunk,
                "priority_score": float(
                    topic.get("priority_score", 0)
                ),
                "reason": topic.get(
                    "reason",
                    "Scheduled according to calculated priority."
                )
            })

            minutes_left -= chunk
            daily_usage[day_index] += chunk

    return plan


# ==================================================
# CALCULATE DAILY WORKLOAD
# ==================================================

def calculate_daily_workload(
    schedule: list[dict]
) -> dict:

    workload = {}

    for item in schedule:

        day = item["day"]

        workload[day] = (
            workload.get(day, 0)
            + int(item["duration_minutes"])
        )

    return workload


# ==================================================
# CALCULATE REMAINING DAILY TIME
# ==================================================

def calculate_remaining_daily_time(
    schedule: list[dict],
    available_minutes: int,
    days: int,
    start_date: date | None = None
) -> dict:

    if available_minutes <= 0 or days <= 0:
        raise ValueError("Invalid study-time constraints.")

    if start_date is None:
        start_date = date.today()

    workload = calculate_daily_workload(schedule)

    return {
        (start_date + timedelta(days=i)).isoformat(): max(
            0,
            available_minutes - workload.get(
                (start_date + timedelta(days=i)).isoformat(),
                0
            )
        )
        for i in range(days)
    }