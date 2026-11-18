"""HTTP endpoints for analytics."""
from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# TODO: Add endpoints. Keep calculations in service.py, not in this file.
