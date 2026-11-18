"""Dynamic priority calculation for intelligent study scheduling."""


def calculate_priority(topic: dict) -> float:
    """
    Calculate dynamic topic priority.

    Higher score means the topic should be considered earlier.

    Factors:
    - Exam urgency
    - Topic difficulty
    - Learning confidence
    - Completion percentage
    - Examination weight
    - Learning speed
    - Missed sessions
    - Revision requirements
    """

    days = max(int(topic.get("days_to_exam", 30)), 0)

    difficulty = max(
        1,
        min(5, int(topic.get("difficulty", 3)))
    )

    confidence = max(
        1,
        min(5, int(topic.get("confidence", 3)))
    )

    completion = max(
        0.0,
        min(100.0, float(topic.get("completion_percent", 0)))
    )

    weight = max(
        0.1,
        float(topic.get("exam_weight", 1.0))
    )

    learning_speed = max(
        0.1,
        float(topic.get("learning_speed", 1.0))
    )

    missed_sessions = max(
        0,
        int(topic.get("missed_sessions", 0))
    )

    revision_due = bool(
        topic.get("revision_due", False)
    )

    urgency = 1 / (days + 1)

    weakness = (6 - confidence) / 5

    unfinished = (100 - completion) / 100

    difficulty_factor = difficulty / 5

    missed_factor = min(missed_sessions / 3, 1.0)

    revision_factor = 1.0 if revision_due else 0.0

    learning_factor = min(
        1.0 / learning_speed,
        2.0
    )

    priority = weight * (
        4 * urgency
        + 2 * weakness
        + 2 * unfinished
        + difficulty_factor
        + missed_factor
        + revision_factor
        + learning_factor
    )

    return round(priority, 4)