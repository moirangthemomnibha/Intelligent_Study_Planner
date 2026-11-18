from app.planning.scheduler import build_schedule

def test_scheduler_respects_horizon_and_positive_duration():
    result = build_schedule([{"id": 1, "name": "Networks", "estimated_minutes": 120}], 60, 2)
    assert sum(item["duration_minutes"] for item in result) == 120
    assert all(item["duration_minutes"] > 0 for item in result)
