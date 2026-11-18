"""
Intelligent Adaptive Multi-Day Study Scheduler.

Features:
1. Multi-day study distribution.
2. Daily study-time protection.
3. Maximum 90-minute sessions.
4. Completion-aware scheduling.
5. Priority-based topic allocation.
6. Flexible planning horizon.
7. Learning-speed adjustment.
8. Revision support.
9. Daily workload balancing.
10. Scheduling explanations.
"""

from datetime import date, timedelta
from math import ceil


MAX_SESSION_MINUTES = 90


def build_schedule(
    topics: list[dict],
    available_minutes: int,
    days: int,
    start_date: date | None = None
) -> list[dict]:

    # ==========================================
    # 1. VALIDATE INPUTS
    # ==========================================

    if available_minutes <= 0:
        raise ValueError(
            "available_minutes must be greater than zero"
        )

    if days <= 0:
        raise ValueError(
            "days must be greater than zero"
        )

    if start_date is None:
        start_date = date.today()

    plan = []

    daily_usage = [0] * days

    # ==========================================
    # 2. PREPARE TOPICS
    # ==========================================

    prepared_topics = []

    for topic in topics:

        completion = max(
            0.0,
            min(
                100.0,
                float(topic.get("completion_percent", 0))
            )
        )

        if completion >= 100:
            continue

        estimated_minutes = max(
            0,
            int(topic.get("estimated_minutes", 0))
        )

        if estimated_minutes <= 0:
            continue

        learning_speed = max(
            0.1,
            float(topic.get("learning_speed", 1.0))
        )

        remaining_minutes = ceil(
            estimated_minutes
            * (100 - completion) / 100
            * learning_speed
        )

        prepared_topics.append({
            **topic,
            "remaining_minutes": remaining_minutes
        })

    # ==========================================
    # 3. SORT TOPICS BY PRIORITY
    # ==========================================

    prepared_topics.sort(
        key=lambda topic: float(
            topic.get("priority_score", 0)
        ),
        reverse=True
    )

    # ==========================================
    # 4. GENERATE DAILY SCHEDULE
    # ==========================================

    for topic in prepared_topics:

        minutes_left = topic["remaining_minutes"]

        for day_index in range(days):

            if minutes_left <= 0:
                break

            remaining_daily_time = (
                available_minutes - daily_usage[day_index]
            )

            if remaining_daily_time <= 0:
                continue

            chunk = min(
                minutes_left,
                remaining_daily_time,
                MAX_SESSION_MINUTES
            )

            if chunk <= 0:
                continue

            session_date = (
                start_date + timedelta(days=day_index)
            )

            # ==================================
            # 5. GENERATE EXPLANATION
            # ==================================

            reason = topic.get(
                "reason",
                "Scheduled according to calculated priority."
            )

            if topic.get("revision_due"):
                reason += " Revision is due."

            if topic.get("missed_sessions", 0) > 0:
                reason += " Includes recovery from missed sessions."

            if topic.get("learning_speed", 1.0) > 1.2:
                reason += " Additional time allocated based on learning speed."

            # ==================================
            # 6. ADD STUDY SESSION
            # ==================================

            plan.append({

                "topic_id": topic.get("id"),

                "topic_name": topic.get(
                    "name",
                    "Untitled topic"
                ),

                "day": session_date.isoformat(),

                "duration_minutes": chunk,

                "priority_score": float(
                    topic.get("priority_score", 0)
                ),

                "reason": reason

            })

            minutes_left -= chunk

            daily_usage[day_index] += chunk

    return plan


# ==============================================
# 7. CALCULATE DAILY WORKLOAD
# ==============================================

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


# ==============================================
# 8. DETECT UNUSED STUDY TIME
# ==============================================

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

    remaining_time = {}

    for index in range(days):

        current_date = (
            start_date + timedelta(days=index)
        ).isoformat()

        remaining_time[current_date] = max(
            0,
            available_minutes - workload.get(current_date, 0)
        )

    return remaining_time