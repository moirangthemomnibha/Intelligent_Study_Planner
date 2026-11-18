"""HTTP endpoints for reports."""
from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])

# TODO: Add endpoints. Keep calculations in service.py, not in this file.
