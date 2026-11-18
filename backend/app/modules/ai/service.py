"""
Deterministic AI recommendation engine.

Analyzes student topic progress and recommends
the next topic to study.
"""

from app.planning.priority import calculate_priority


def recommend_next_action(student_summary: dict) -> dict:
    """
    Recommend the next study action based on topic priority.
    """

    topics = student_summary.get("topics", [])

    if not topics:
        return {
            "recommendation": "Add subjects and topics to your study planner first.",
            "reasons": [
                "There are no topics available for analysis."
            ],
        }

    unfinished_topics = [
        topic for topic in topics
        if float(topic.get("completion_percent", 0)) < 100
    ]

    if not unfinished_topics:
        return {
            "recommendation": "Excellent work! All your topics are completed.",
            "reasons": [
                "There are no unfinished topics remaining."
            ],
        }

    ranked_topics = sorted(
        unfinished_topics,
        key=calculate_priority,
        reverse=True
    )

    best_topic = ranked_topics[0]

    topic_name = best_topic.get("name", "your highest-priority topic")
    completion = float(best_topic.get("completion_percent", 0))
    confidence = int(best_topic.get("confidence", 3))
    difficulty = int(best_topic.get("difficulty", 3))
    days_to_exam = int(best_topic.get("days_to_exam", 30))

    reasons = []

    if days_to_exam <= 7:
        reasons.append("The exam is approaching.")

    if confidence <= 2:
        reasons.append("Your confidence in this topic is low.")

    if difficulty >= 4:
        reasons.append("This topic has a high difficulty level.")

    if completion < 50:
        reasons.append("A significant portion of this topic is unfinished.")

    if not reasons:
        reasons.append(
            "This topic has the highest calculated priority among unfinished topics."
        )

    return {
        "recommendation": f"Study {topic_name} next.",
        "reasons": reasons,
    }