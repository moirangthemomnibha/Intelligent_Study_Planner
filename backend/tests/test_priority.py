from app.planning.priority import calculate_priority

def test_urgent_weak_incomplete_topic_scores_higher():
    urgent = {"days_to_exam": 1, "difficulty": 5, "confidence": 1, "completion_percent": 10}
    relaxed = {"days_to_exam": 30, "difficulty": 2, "confidence": 5, "completion_percent": 90}
    assert calculate_priority(urgent) > calculate_priority(relaxed)
