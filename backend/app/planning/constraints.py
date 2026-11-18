"""Validate and manage intelligent study planner constraints."""

MAX_PLAN_DAYS = 30
MAX_ASSESSMENTS = 10
REVISION_MINUTES = 30
MAX_TOPIC_HOURS_PER_DAY = 1.0
ASSESSMENT_DAILY_SHARE = 0.60
EPSILON = 0.000001

MAX_SESSION_MINUTES = 90
MIN_SESSION_MINUTES = 1


def validate_session(
    session: dict,
    daily_limit_minutes: int
) -> list[str]:

    issues = []

    duration = int(session.get("duration_minutes", 0))

    if duration <= 0:
        issues.append("Session duration must be positive.")

    if duration > MAX_SESSION_MINUTES:
        issues.append(
            "Session exceeds the recommended 90-minute block."
        )

    if duration > daily_limit_minutes:
        issues.append(
            "Session exceeds the student's daily available time."
        )

    return issues


def validate_schedule(
    schedule: list[dict],
    daily_limit_minutes: int
) -> list[str]:

    issues = []
    daily_totals = {}

    for index, item in enumerate(schedule):

        session_issues = validate_session(
            item,
            daily_limit_minutes
        )

        for issue in session_issues:
            issues.append(f"Session {index + 1}: {issue}")

        day = item.get("day")
        duration = int(item.get("duration_minutes", 0))

        daily_totals[day] = (
            daily_totals.get(day, 0) + duration
        )

    for day, total in daily_totals.items():

        if total > daily_limit_minutes:
            issues.append(
                f"Daily limit exceeded on {day}: "
                f"{total}/{daily_limit_minutes} minutes."
            )

    return issues


def validate_plan_settings(
    available_minutes: int,
    days: int,
    buffer_minutes: int = 0
) -> list[str]:

    issues = []

    if available_minutes <= 0:
        issues.append(
            "Daily available study time must be positive."
        )

    if days < 1 or days > MAX_PLAN_DAYS:
        issues.append(
            f"Planning duration must be between 1 and {MAX_PLAN_DAYS} days."
        )

    if buffer_minutes < 0:
        issues.append(
            "Buffer minutes cannot be negative."
        )

    if buffer_minutes >= available_minutes:
        issues.append(
            "Buffer time must be less than daily available study time."
        )

    return issues


def validate_duplicate_sessions(
    schedule: list[dict]
) -> list[str]:

    issues = []
    seen = set()

    for item in schedule:

        key = (
            item.get("topic_id"),
            item.get("day")
        )

        if key in seen:
            issues.append(
                f"Duplicate topic session detected: {key}"
            )
        else:
            seen.add(key)

    return issues